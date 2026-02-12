from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
from app.database import Base

class RepoAnalysis(Base):
    __tablename__ = "repo_analysis"

    id = Column(Integer, primary_key=True, index=True)
    repo_url = Column(String, index=True)
    score = Column(Integer)
    message = Column(String)
    features = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
