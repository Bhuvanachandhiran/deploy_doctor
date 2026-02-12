from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from app.github_client import extract_repo_info, get_repo_tree
from app.feature_extractor import extract_features
from app.database import init_db, SessionLocal, Analysis

app = FastAPI(title="DeployDoctor API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        with SessionLocal() as db:
            analysis = Analysis(
                repo_url=repo_url,
                features=features,
                score=score,
                scoring_version=SCORING_VERSION
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            
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
    with SessionLocal() as db:
        total = db.query(Analysis).count()
        if total == 0:
            return {"total_analyses": 0, "average_score": 0}

        avg_score_data = db.query(Analysis).with_entities(Analysis.score).all()
        avg = sum([s[0] for s in avg_score_data]) / total

        return {
            "total_analyses": total,
            "average_score": round(avg, 2)
        }

def calculate_score(features):
    score = 0
    if features.get("has_readme"): score += 15
    if features.get("has_requirements"): score += 20
    if features.get("has_dockerfile"): score += 25
    if features.get("has_ci_cd"): score += 25
    if features.get("has_dockerfile") and features.get("has_ci_cd"): score += 15
    return min(score, 100)

def interpret_score(score: int) -> str:
    if score >= 75: return "Production Ready"
    elif score >= 50: return "Almost Ready"
    elif score >= 25: return "Needs Improvement"
    return "Not Deployment Ready"
