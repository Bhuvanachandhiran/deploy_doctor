from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
from sqlalchemy import func
from app.github_client import extract_repo_info, get_repo_tree
from app.feature_extractor import extract_features
from app.database import init_db, SessionLocal
from app.models import RepoAnalysis

app = FastAPI(title="DeployDoctor API")

# -------------------------
# CORS Configuration
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCORING_VERSION = "v1.2"


# -------------------------
# Startup Event
# -------------------------
@app.on_event("startup")
def on_startup():
    init_db()


# -------------------------
# Request & Response Schemas
# -------------------------
class RepoRequest(BaseModel):
    repo_url: str


class AnalysisResponse(BaseModel):
    analysis_id: int
    repo_url: str
    scoring_version: str
    features: Dict
    score: int
    message: str


class StatsResponse(BaseModel):
    total_analyses: int
    average_score: float


class HistoryItem(BaseModel):
    analysis_id: int
    repo_url: str
    score: int
    message: str


# -------------------------
# Health Check
# -------------------------
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# -------------------------
# Analyze Endpoint
# -------------------------
@app.post("/analyze")
def analyze_repo(request: RepoRequest):
    repo_url = request.repo_url

    with SessionLocal() as db:

        # 1️⃣ Check if repo already analyzed
        existing = db.query(RepoAnalysis).filter_by(repo_url=repo_url).first()
        if existing:
            suggestions = generate_suggestions(existing.features)
            return {
                "analysis_id": existing.id,
                "repo_url": existing.repo_url,
                "scoring_version": SCORING_VERSION,
                "features": existing.features,
                "score": existing.score,
                "message": existing.message,
                "suggestions": suggestions,
                "cached": True
            }

        # 2️⃣ If not cached → analyze fresh
        try:
            owner, repo = extract_repo_info(repo_url)
            tree_json = get_repo_tree(owner, repo)
            features = extract_features(tree_json)
            score = calculate_score(features)
            message = interpret_score(score)
            suggestions = generate_suggestions(features)


            analysis = RepoAnalysis(
                repo_url=repo_url,
                score=score,
                message=message,
                features=features
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
                "message": message,
                "suggestions": suggestions,
                "cached": False
            }

        except Exception as e:
            return {"error": str(e)}

# -------------------------
# Stats Endpoint
# -------------------------
@app.get("/stats", response_model=StatsResponse)
def get_stats():
    with SessionLocal() as db:
        total = db.query(RepoAnalysis).count()

        if total == 0:
            return StatsResponse(total_analyses=0, average_score=0)

        avg_score = db.query(func.avg(RepoAnalysis.score)).scalar()

        return StatsResponse(
            total_analyses=total,
            average_score=round(avg_score, 2)
        )


# -------------------------
# History Endpoint
# -------------------------
@app.get("/history")
def get_history(limit: int = 10):
    with SessionLocal() as db:
        analyses = (
            db.query(RepoAnalysis)
            .order_by(RepoAnalysis.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": a.id,
                "repo_url": a.repo_url,
                "score": a.score,
                "message": a.message,
                "created_at": a.created_at.isoformat()
            }
            for a in analyses
        ]

# -------------------------
# Scoring Logic
# -------------------------
def calculate_score(features: Dict) -> int:
    score = 0
    if features.get("has_readme"): score += 15
    if features.get("has_requirements"): score += 20
    if features.get("has_dockerfile"): score += 25
    if features.get("has_ci_cd"): score += 25
    if features.get("has_dockerfile") and features.get("has_ci_cd"): score += 15
    return min(score, 100)


def interpret_score(score: int) -> str:
    if score >= 75:
        return "Production Ready"
    elif score >= 50:
        return "Almost Ready"
    elif score >= 25:
        return "Needs Improvement"
    return "Not Deployment Ready"
def generate_suggestions(features: Dict) -> list:
    suggestions = []

    if not features.get("has_readme"):
        suggestions.append("Add a README.md explaining setup, usage, and purpose.")

    if not features.get("has_requirements"):
        suggestions.append("Add a requirements.txt file for dependency management.")

    if not features.get("has_dockerfile"):
        suggestions.append("Create a Dockerfile to make deployment portable.")

    if not features.get("has_ci_cd"):
        suggestions.append("Add CI/CD using GitHub Actions for automated testing and deployment.")

    if features.get("has_readme") and not features.get("has_ci_cd"):
        suggestions.append("Consider adding a build badge in your README.")

    if not suggestions:
        suggestions.append("Your repository follows strong deployment practices.")

    return suggestions
