from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
from app.github_client import extract_repo_info, get_repo_tree
from app.feature_extractor import extract_features
from app.database import init_db, SessionLocal, Analysis

app = FastAPI(title="DeployDoctor API")

# Initialize database tables
init_db()

SCORING_VERSION = "v1.1"

class RepoRequest(BaseModel):
    repo_url: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/analyze")
def analyze_repo(request: RepoRequest):
    repo_url = request.repo_url
    try:
        owner, repo = extract_repo_info(repo_url)
        tree_json = get_repo_tree(owner, repo)
        features = extract_features(tree_json)
        score = calculate_score(features)

        # Store Analysis Result in DB
        db = SessionLocal()
        analysis = Analysis(
            repo_url=repo_url,
            features=features,
            score=score,
            scoring_version=SCORING_VERSION
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        db.close()

        return {
            "analysis_id": analysis.id,
            "repo_url": repo_url,
            "scoring_version": SCORING_VERSION,
            "features": features,
            "score": score,
            "message": interpret_score(score)
        }
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/stats")
def get_stats():
    db = SessionLocal()
    try:
        total = db.query(Analysis).count()
        avg_score_data = db.query(Analysis).with_entities(Analysis.score).all()

        if total == 0:
            return {"total_analyses": 0, "average_score": 0}

        # Calculate average from tuples returned by .all()
        avg = sum([s[0] for s in avg_score_data]) / total

        return {
            "total_analyses": total,
            "average_score": round(avg, 2)
        }
    finally:
        db.close()

def calculate_score(features):
    score = 0
    if features["has_readme"]: score += 15
    if features["has_requirements"]: score += 20
    if features["has_dockerfile"]: score += 25
    if features["has_ci_cd"]: score += 25
    if features["has_dockerfile"] and features["has_ci_cd"]: score += 15
    return min(score, 100)

def interpret_score(score: int) -> str:
    if score >= 75: return "Production Ready"
    elif score >= 50: return "Almost Ready"
    elif score >= 25: return "Needs Improvement"
    return "Not Deployment Ready"
