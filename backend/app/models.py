from sqlalchemy import Column, Integer, String, JSON
from app.database import Base

class RepoAnalysis(Base):
    __tablename__ = "repo_analysis"

    id = Column(Integer, primary_key=True, index=True)
    repo_url = Column(String, nullable=False)
    score = Column(Integer)
    message = Column(String)
    features = Column(JSON)
