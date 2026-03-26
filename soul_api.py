from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SoulAPI")

app = FastAPI(title="Andile Soul API", version="1.0.0")
security = HTTPBearer()

# Enable CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_TOKEN = "andile_dev_secret_2026"
STATE_PATH = Path("C:/Users/molel/Soul/soul_state.json")

def verify_token(auth: HTTPAuthorizationCredentials = Security(security)):
    if auth.credentials != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid API Token")
    return auth.credentials

def get_state():
    if not STATE_PATH.exists():
        return {
            "status": "Offline",
            "current_mission": "None",
            "completed_today": [],
            "repo_queue": [],
            "stats": {
                "jobs_applied": 0,
                "emails_sent": 0,
                "responses": 0,
                "income": 0,
                "prs_made": 0,
                "prs_merged": 0,
                "bounties_claimed": 0
            }
        }
    with open(STATE_PATH, "r") as f:
        return json.load(f)

@app.get("/api/status", dependencies=[Depends(verify_token)])
async def get_status():
    state = get_state()
    return {
        "participants": {
            "andile": {
                "status": state.get("status", "Active"),
                "mission": state.get("current_mission", "Idle")
            }
        },
        "activity_log": state.get("activity_log", []),
        "tasks": state.get("tasks", [])
    }

@app.get("/api/queue", dependencies=[Depends(verify_token)])
async def get_queue():
    state = get_state()
    return {
        "status": {
            "pending": len(state.get("repo_queue", [])),
            "in_progress": 1 if state.get("status") != "Idle" else 0,
            "completed_today": len(state.get("completed_today", [])),
            "failed_today": state.get("failed_today", 0)
        },
        "pending_tasks": [{"type": repo, "priority": 3} for repo in state.get("repo_queue", [])[:10]]
    }

@app.get("/api/email_stats", dependencies=[Depends(verify_token)])
async def get_email_stats():
    state = get_state()
    stats = state.get("stats", {})
    sent = stats.get("emails_sent", 0)
    return {
        "daily": {
            "sent": sent,
            "limit": 500,
            "remaining": 500 - sent
        },
        "hourly": {"sent": state.get("emails_this_hour", 0)},
        "total": {"sent": stats.get("total_emails_sent", sent)}
    }

@app.get("/api/contributions", dependencies=[Depends(verify_token)])
async def get_contributions():
    state = get_state()
    stats = state.get("stats", {})
    return {
        "prs_open": stats.get("prs_made", 0) - stats.get("prs_merged", 0),
        "prs_merged": stats.get("prs_merged", 0),
        "prs_closed": 0,
        "target_repos": len(state.get("completed_today", [])) + len(state.get("repo_queue", [])),
        "bounties_claimed": stats.get("bounties_claimed", 0),
        "open_prs": []
    }

@app.get("/api/jobs", dependencies=[Depends(verify_token)])
async def get_jobs():
    # Load from jobs_applied.json if exists
    jobs_path = Path("C:/Users/molel/Soul/jobs_applied.json")
    if jobs_path.exists():
        with open(jobs_path, "r") as f:
            return {"jobs": json.load(f)}
    return {"jobs": []}

@app.get("/api/github", dependencies=[Depends(verify_token)])
async def get_github():
    return {
        "followers": 10, # Mock or fetch
        "public_repos": 55
    }

@app.get("/api/prs", dependencies=[Depends(verify_token)])
async def get_prs():
    state = get_state()
    stats = state.get("stats", {})
    return {
        "total": stats.get("prs_made", 0),
        "merged": stats.get("prs_merged", 0)
    }

@app.get("/api/health", dependencies=[Depends(verify_token)])
async def get_health():
    return {
        "services": {
            "ollama": True,
            "impossible_cloud": True
        }
    }

@app.get("/api/crypto", dependencies=[Depends(verify_token)])
async def get_crypto():
    state = get_state()
    stats = state.get("stats", {})
    return {
        "strategies_count": 3,
        "airdrops_claimed": stats.get("bounties_claimed", 0),
        "total_crypto_earnings": 0,
        "total_earned": 0
    }

class ChatMessage(BaseModel):
    message: str

@app.post("/api/chat", dependencies=[Depends(verify_token)])
async def chat(msg: ChatMessage):
    # This would call Andile's brain
    return {"response": f"I received your message: '{msg.message}'. I am currently processing the Pulse Protocol."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
