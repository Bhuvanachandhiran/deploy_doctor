import requests
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

GITHUB_API_BASE = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
}

def extract_repo_info(repo_url: str):
    parsed = urlparse(repo_url)
    parts = parsed.path.strip("/").replace(".git", "").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")
    return parts[0], parts[1]

def get_repo_tree(owner: str, repo: str):
    repo_info_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    repo_info = requests.get(repo_info_url, headers=HEADERS).json()

    default_branch = repo_info.get("default_branch", "main")

    branch_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/branches/{default_branch}"
    branch_info = requests.get(branch_url, headers=HEADERS).json()
    commit_sha = branch_info["commit"]["sha"]

    tree_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{commit_sha}?recursive=1"
    response = requests.get(tree_url, headers=HEADERS)

    return response.json()
