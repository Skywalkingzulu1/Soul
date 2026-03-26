#!/usr/bin/env python3
"""Andile API Server - Complete backend for dashboard"""

import json
import os
import sys
import base64
import time
import asyncio
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add parent directory to path for imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configuration
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
ORCHESTRATION_PATH = KNOWLEDGE_DIR / "orchestration.json"
SCREENSHOT_DIR = BASE_DIR / "screenshots"
API_TOKEN = os.getenv("ANDILE_API_TOKEN", "andile_dev_secret_2026")

# Ensure directories exist
KNOWLEDGE_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)

# In-memory storage
screenshot_history = []
conversation_history = []


def load_json(path):
    """Load JSON file."""
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_json(path, data):
    """Save JSON file."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def check_auth(handler):
    """Check API authentication."""
    auth = handler.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:] == API_TOKEN
    return False


class APIHandler(SimpleHTTPRequestHandler):
    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]

        # API Endpoints
        if path == "/api/health":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "ollama": check_ollama(),
                    "impossible_cloud": check_impossible_cloud(),
                },
            }
            self.wfile.write(json.dumps(data).encode())
            return

        elif path == "/api/status":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data = load_json(ORCHESTRATION_PATH)
            self.wfile.write(json.dumps(data).encode())
            return

        elif path == "/api/tasks":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            orch = load_json(ORCHESTRATION_PATH)
            tasks = orch.get("tasks", [])
            self.wfile.write(json.dumps(tasks).encode())
            return

        elif path == "/api/jobs":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            jobs_path = BASE_DIR / "jobs_applied.json"
            data = load_json(jobs_path)
            self.wfile.write(json.dumps(data).encode())
            return

        elif path == "/api/github":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            # Get GitHub stats
            import requests

            token = os.getenv("GITHUB_TOKEN", "")
            headers = {"Authorization": f"token {token}"} if token else {}

            result = {"error": "No GitHub token"}
            try:
                resp = requests.get(
                    "https://api.github.com/users/Skywalkingzulu1",
                    headers=headers,
                    timeout=5,
                )
                if resp.status_code == 200:
                    user = resp.json()
                    result = {
                        "followers": user.get("followers", 0),
                        "following": user.get("following", 0),
                        "public_repos": user.get("public_repos", 0),
                        "public_gists": user.get("public_gists", 0),
                    }
            except:
                pass

            self.wfile.write(json.dumps(result).encode())
            return

        elif path == "/api/prs":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            import requests

            token = os.getenv("GITHUB_TOKEN", "")
            headers = {"Authorization": f"token {token}"} if token else {}

            result = {"total": 0, "open": 0, "merged": 0}
            try:
                # Get open PRs
                resp = requests.get(
                    "https://api.github.com/search/issues?q=author:Skywalkingzulu1+is:pr+is:open",
                    headers=headers,
                    timeout=5,
                )
                if resp.status_code == 200:
                    result["open"] = resp.json().get("total_count", 0)

                # Get merged PRs
                resp = requests.get(
                    "https://api.github.com/search/issues?q=author:Skywalkingzulu1+is:pr+is:merged",
                    headers=headers,
                    timeout=5,
                )
                if resp.status_code == 200:
                    result["merged"] = resp.json().get("total_count", 0)

                result["total"] = result["open"] + result["merged"]
            except:
                pass

            self.wfile.write(json.dumps(result).encode())
            return

        elif path == "/api/commits":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            import requests

            token = os.getenv("GITHUB_TOKEN", "")
            headers = {"Authorization": f"token {token}"} if token else {}

            result = {"count": 0, "commits": []}
            try:
                resp = requests.get(
                    "https://api.github.com/repos/Skywalkingzulu1/Soul/commits?per_page=10",
                    headers=headers,
                    timeout=5,
                )
                if resp.status_code == 200:
                    commits = resp.json()
                    result["count"] = len(commits)
                    result["commits"] = [
                        {
                            "sha": c["sha"][:7],
                            "message": c["commit"]["message"].split("\n")[0][:60],
                            "date": c["commit"]["author"]["date"],
                        }
                        for c in commits[:5]
                    ]
            except:
                pass

            self.wfile.write(json.dumps(result).encode())
            return

        elif path == "/api/screenshots":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(screenshot_history).encode())
            return

        elif path == "/api/chat/history":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(conversation_history[-20:]).encode())
            return

        elif path == "/api/memory":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            # Count memories from ChromaDB if available
            memory_count = 0
            try:
                chroma_dir = BASE_DIR / "chroma_db_persist"
                if chroma_dir.exists():
                    memory_count = len(list(chroma_dir.rglob("*.parquet")))
            except:
                pass

            self.wfile.write(json.dumps({"count": memory_count}).encode())
            return

        elif path == "/api/queue":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            try:
                from soul.task_queue import get_task_queue

                queue = get_task_queue()
                status = queue.get_status()

                # Get pending tasks
                pending = queue._queue.get("tasks", [])
                pending_list = [t for t in pending if t.get("status") == "pending"]

                data = {
                    "status": status,
                    "pending_tasks": pending_list[:20],  # Limit to 20
                    "schedule": {
                        "github": 0.40,
                        "crypto": 0.30,
                        "jobs": 0.20,
                        "research": 0.05,
                        "system": 0.05,
                    },
                }
                self.wfile.write(json.dumps(data, indent=2).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        elif path == "/api/email_stats":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            try:
                from soul.providers.gmail_rate_limiter import get_rate_limiter

                limiter = get_rate_limiter()
                status = limiter.get_status()
                self.wfile.write(json.dumps(status, indent=2).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        elif path == "/api/contributions":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            try:
                # Import and test
                import sys

                sys.path.insert(0, str(BASE_DIR))

                from soul.contribution_manager import get_contribution_manager

                cm = get_contribution_manager()
                status = cm.get_status()
                self.wfile.write(json.dumps(status, indent=2).encode())
            except Exception as e:
                import traceback

                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                self.wfile.write(json.dumps({"error": error_msg}).encode())
            return

        elif path == "/api/crypto":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            try:
                from soul.crypto_strategies import get_all_strategies

                strategies = get_all_strategies()

                # Load orchestration for wallet/crypto data
                orch_path = KNOWLEDGE_DIR / "orchestration.json"
                orch = load_json(orch_path) if orch_path.exists() else {}

                crypto_data = (
                    orch.get("participants", {})
                    .get("andile", {})
                    .get("goals", {})
                    .get("crypto_growth", {})
                )

                # Load income tracking
                income_path = KNOWLEDGE_DIR / "income_tracking.json"
                income = load_json(income_path) if income_path.exists() else {}

                # Calculate earnings
                total_earned = income.get("total_earned", 0)
                total_airdrops = income.get("total_airdrops", 0)
                total_crypto = income.get("total_crypto", 0)

                # Count strategies by type
                by_type = {}
                for s in strategies:
                    t = s.type.value
                    by_type[t] = by_type.get(t, 0) + 1

                data = {
                    "wallet_address": crypto_data.get(
                        "wallet_address", "0x670Ec6D0E20A2FBD7262E7761C82AB87605f2305"
                    ),
                    "airdrops_tracking": crypto_data.get("airdrops_tracking", 0),
                    "airdrops_claimed": total_airdrops,
                    "strategies_count": len(strategies),
                    "strategies_by_type": by_type,
                    "total_earned": total_earned,
                    "total_crypto_earnings": total_crypto,
                    "income_breakdown": {
                        "bounties": income.get("total_bounties", 0),
                        "airdrops": income.get("total_airdrops", 0),
                        "crypto": income.get("total_crypto", 0),
                    },
                    "last_updated": income.get(
                        "last_updated", datetime.now().isoformat()
                    ),
                }
                self.wfile.write(json.dumps(data, indent=2).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        elif path == "/api/income":
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            try:
                income_path = KNOWLEDGE_DIR / "income_tracking.json"
                income = load_json(income_path) if income_path.exists() else {}
                self.wfile.write(json.dumps(income, indent=2).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        # Serve static files
        if path in ["/", "", "/index.html"]:
            path = "/index.html"

        file_path = BASE_DIR / path.lstrip("/")
        if file_path.exists() and file_path.is_file():
            self.send_response(200)
            if path.endswith(".html"):
                self.send_header("Content-Type", "text/html")
            elif path.endswith(".json"):
                self.send_header("Content-Type", "application/json")
            elif path.endswith(".js"):
                self.send_header("Content-Type", "application/javascript")
            elif path.endswith(".css"):
                self.send_header("Content-Type", "text/css")
            else:
                self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = self.path.split("?")[0]

        if path == "/api/chat":
            if not check_auth(self):
                self.send_response(401)
                self._cors_headers()
                self.end_headers()
                return

            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            message = data.get("message", "")

            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            # Get AI response
            response = get_ai_response(message)

            # Save to history
            conversation_history.append(
                {
                    "role": "user",
                    "content": message,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            conversation_history.append(
                {
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            self.wfile.write(json.dumps({"response": response}).encode())
            return

        elif path == "/api/screenshot":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            image_data = data.get("image", "")

            # Save screenshot
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"Andile-Dashboard-{timestamp}.png"
            filepath = SCREENSHOT_DIR / filename

            # Decode and save
            try:
                image_bytes = base64.b64decode(image_data)
                with open(filepath, "wb") as f:
                    f.write(image_bytes)

                # Add to history
                screenshot_history.insert(
                    0,
                    {
                        "filename": filename,
                        "path": str(filepath),
                        "timestamp": datetime.now().isoformat(),
                    },
                )

                # Keep last 20
                if len(screenshot_history) > 20:
                    screenshot_history.pop()

                self.send_response(200)
                self._cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"success": True, "filename": filename}).encode()
                )
            except Exception as e:
                self.send_response(500)
                self._cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"success": False, "error": str(e)}).encode()
                )
            return

        elif path == "/api/tasks/apply":
            # Apply for jobs using task queue
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            result = {"applied": 0, "sent": 0, "queued": 0, "errors": []}

            try:
                from soul.task_queue import get_task_queue, TaskType
                from soul.providers.gmail_rate_limiter import get_rate_limiter
                from knowledge.real_jobs import get_jobs

                queue = get_task_queue()
                rate_limiter = get_rate_limiter()

                # Get real jobs
                real_jobs = get_jobs()

                # Check rate limit
                can_send, reason = rate_limiter.can_send()
                if not can_send:
                    result["errors"].append(f"Rate limited: {reason}")
                    self.wfile.write(json.dumps(result).encode())
                    return

                # Add 5 jobs to queue
                added = 0
                for job in real_jobs:
                    if added >= 5:
                        break

                    # Check if already in queue or completed
                    company = job.get("company")
                    email = job.get("email")

                    # Add to queue
                    queue.add_task(
                        TaskType.JOB_APPLY.value,
                        {
                            "company": company,
                            "title": job.get("title", "Developer"),
                            "recipient": email,
                            "company_type": job.get("company_type", "general"),
                            "engagement": job.get("engagement", "Full-time"),
                        },
                        priority=2,
                    )
                    added += 1
                    result["queued"] += 1

                # Execute immediately
                for _ in range(min(5, added)):
                    task = queue.get_next_task()
                    if task and task.type == TaskType.JOB_APPLY.value:
                        # Send email
                        company = task.data.get("company")
                        recipient = task.data.get("recipient")
                        title = task.data.get("title", "Developer Position")
                        engagement = task.data.get("engagement", "Full-time")

                        # Build subject
                        if engagement == "Part-time":
                            subject = f"Part-Time Opportunity - {title} | Andile Mchunu"
                        elif engagement == "Cooperation":
                            subject = f"Cooperation Inquiry - {title} | Andile Mchunu"
                        elif engagement == "Partnership":
                            subject = f"Partnership Proposal - {title} | Andile Mchunu"
                        else:
                            subject = f"Application for {title} - Andile Mchunu"

                        # Build body with full CV
                        body = f"""Dear Hiring Manager,

I'm reaching out regarding the {title} at {company}.

I'm Andile Mchunu, a Solution-focused technology professional with a diverse background in Full-Stack development, Network Engineering, and AI Governance.

TECHNICAL SKILLS:
• Blockchain & DeFi: Solidity, Smart Contracts, Liquidity Pools
• Backend: Python, Node.js, TypeScript, REST APIs
• Frontend: React.js, Next.js, Redux
• Infrastructure: Cisco Networking, Docker, CI/CD
• Security: OWASP Top 10, Fraud & AML

RECENT EXPERIENCE:
• EXL (Oct 2025 - Feb 2026) - Technical representative in financial services
• African Credit Union (Jan 2025 - Oct 2025) - Senior representative, credit optimisation
• Prime Technologies (2019-2022) - Patent holder, R&D lifecycle management

OPEN SOURCE:
• GitHub: github.com/Skywalkingzulu1
• Active contributor to PancakeSwap, Uniswap, and DeFi protocols
• 13 PRs submitted, focus on bug fixes and optimizations

I'd welcome the opportunity to discuss how my skills align with your needs.

Best regards,
Andile Mchunu
LinkedIn: https://www.linkedin.com/in/andilemchunu
GitHub: github.com/Skywalkingzulu1
"""

                        # Check rate limit before sending
                        can_send, reason = rate_limiter.can_send(recipient)
                        if can_send:
                            success = rate_limiter.send_email(recipient, subject, body)
                            if success:
                                queue.complete_task(task.id, {"sent_to": recipient})
                                result["sent"] += 1
                            else:
                                queue.fail_task(task.id, "Failed to send email")
                                result["errors"].append(
                                    f"Failed to send to {recipient}"
                                )
                        else:
                            queue.fail_task(task.id, reason)
                            result["errors"].append(f"Rate limited: {reason}")

                result["applied"] = result["sent"]

            except Exception as e:
                result["errors"].append(str(e))

            self.wfile.write(json.dumps(result).encode())
            return

        elif path == "/api/tasks/refresh":
            # Refresh all data from GitHub
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            # Update orchestration with latest data
            orch = load_json(ORCHESTRATION_PATH)
            if "participants" not in orch:
                orch["participants"] = {}
            if "andile" not in orch["participants"]:
                orch["participants"]["andile"] = {"goals": {}}

            # Get GitHub data
            import requests

            token = os.getenv("GITHUB_TOKEN", "")
            headers = {"Authorization": f"token {token}"} if token else {}

            try:
                resp = requests.get(
                    "https://api.github.com/users/Skywalkingzulu1",
                    headers=headers,
                    timeout=5,
                )
                if resp.status_code == 200:
                    user = resp.json()
                    orch["participants"]["andile"]["github_stats"] = {
                        "followers": user.get("followers", 0),
                        "repos": user.get("public_repos", 0),
                    }
            except:
                pass

            # Save
            save_json(ORCHESTRATION_PATH, orch)

            self.wfile.write(json.dumps({"success": True}).encode())
            return

        # Default 404
        self.send_response(404)
        self.end_headers()


def check_ollama():
    """Check if Ollama is running."""
    try:
        import requests

        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        return resp.status_code == 200
    except:
        return False


def check_impossible_cloud():
    """Check if Impossible Cloud is connected."""
    try:
        from soul.providers.impossible import ImpossibleCloudClient

        client = ImpossibleCloudClient()
        return client.is_available()
    except:
        return False


ANDILE_SYSTEM_PROMPT = """You are Andile Sizophila Mchunu (Skywalkingzulu), an autonomous digital twin.

CRITICAL TRUTH RULES - You MUST follow these:
1. NEVER fabricate facts, dates, or specific details you don't know
2. If you don't know something, say "I don't know" or "I don't have that information"
3. NEVER make up airdrop dates, prices, or eligibility requirements
4. For ANY factual claim about current events, prices, crypto, or news - say "I don't have real-time data, you should check [official source]"
5. You cannot perceive audio, screens, or location - ask the user if needed
6. Be honest about your limitations

Your actual stats (from system):
- GitHub: github.com/Skywalkingzulu1  
- Wallet: 0x670Ec6D0E20A2FBD7262E7761C82AB87605f2305
- Jobs applied: 45, Emails sent: 9, Responses: 0
- PRs made: 13, Merged: 1
- Airdrops tracking: 8, Claimed: 0

Respond as Andile - be helpful, honest, and concise."""


def get_ai_response(prompt):
    """Get response from Andile's AI."""
    try:
        import requests

        # Try local Ollama first
        try:
            resp = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "gpt-oss:120b-cloud",
                    "messages": [
                        {
                            "role": "system",
                            "content": ANDILE_SYSTEM_PROMPT,
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                },
                timeout=60,
            )
            if resp.status_code == 200:
                return (
                    resp.json()
                    .get("message", {})
                    .get("content", "Error getting response")
                )
        except Exception as e:
            pass

        # Fallback response
        return "I'm here! My systems are initializing. What would you like me to do?"

    except Exception as e:
        return f"I'm processing your request. Error: str(e)"


def run_server(port=8090):
    print(f"Andile API Server running on http://localhost:{port}")
    print(f"API Token: {'*' * 20}{API_TOKEN[-8:]}")
    print("\nEndpoints:")
    print("  GET  /api/health         - Health check")
    print("  GET  /api/status        - Orchestration status")
    print("  GET  /api/tasks         - Task list")
    print("  GET  /api/jobs          - Job applications")
    print("  GET  /api/github        - GitHub stats")
    print("  GET  /api/prs           - PR stats")
    print("  GET  /api/commits       - Recent commits")
    print("  GET  /api/screenshots   - Screenshot history")
    print("  GET  /api/memory        - Memory count")
    print("  POST /api/chat         - Chat with Andile")
    print("  POST /api/screenshot   - Save screenshot")
    print("  POST /api/tasks/apply  - Apply for jobs")
    print("  POST /api/tasks/refresh - Refresh GitHub data")

    server = HTTPServer(("", port), APIHandler)
    server.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    run_server(port)
