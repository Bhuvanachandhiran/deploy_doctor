# 🚀 Deploy Doctor

Deploy Doctor is a cloud-deployed backend service that analyzes GitHub repositories and evaluates their deployment readiness.

It scans repositories for essential production indicators such as README, Dockerfile, CI/CD configuration, and dependency files, then assigns a readiness score with improvement suggestions.

Live API:
https://deploy-doctor.onrender.com
live App:
https://deploy-doctor.vercel.app

---

## 🧠 Why This Project?

Many student and personal projects lack deployment best practices.  
Deploy Doctor helps developers understand whether their repository is production-ready.

This project demonstrates:
- Backend API development
- Database integration
- Caching strategy
- Cloud deployment
- Zero-cost infrastructure setup

---

## ⚙️ Tech Stack

Backend:
- FastAPI
- SQLAlchemy
- PostgreSQL (Supabase Free Tier)
- Uvicorn

Infrastructure:
- Render (Free Tier)
- Supabase (Free Postgres)

Other:
- GitHub REST API
- JSON-based feature analysis

---

## 📊 Features

- Analyze GitHub repository structure
- Score deployment readiness (0–100)
- Generate improvement suggestions
- Caching to prevent duplicate analysis
- Historical analysis tracking
- Platform-wide statistics endpoint

---

## 🔍 API Endpoints

### POST /analyze
Analyzes a GitHub repository.

Request:
{
  "repo_url": "https://github.com/user/repo"
}

Response:
- Score
- Deployment status
- Feature breakdown
- Suggestions
- Cached flag

---

### GET /stats
Returns:
- Total analyses
- Average score

---

### GET /history
Returns:
- Recent repository analyses
- Score history

---

## 🧱 Architecture

Client (HTML Frontend)
        ↓
FastAPI Backend
        ↓
Feature Extraction Layer
        ↓
Scoring Engine
        ↓
PostgreSQL (Supabase)

The scoring logic is versioned to allow future scoring improvements.

---

## 💡 Caching Strategy

If a repository has already been analyzed, the system returns the stored result instead of re-analyzing the repository.

This reduces:
- GitHub API calls
- Server computation
- Response time

---

## 🚀 Future Improvements

- Test detection and quality scoring
- GitHub OAuth user login
- Repository activity scoring
- Deployment badge generation
- LLM-based README quality analysis
- Automatic re-scan scheduler
- Security vulnerability scanning

---

## 📌 Author

Built by Bhuvanachandhiran  
Computer Science Graduate | AI & Backend Enthusiast
