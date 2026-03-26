#!/usr/bin/env python3
"""Andile Daemon Runner - Runs Andile autonomously for specified duration.

Usage:
    python daemon_runner.py [hours]
    python daemon_runner.py 4    # Run for 4 hours

The daemon will:
1. Start Ollama if not running
2. Start the Dashboard API on port 8090
3. Initialize Andile Soul with autonomous event loop
4. Run for the specified duration (default: 4 hours)
5. Execute background tasks: job hunts, GitHub bounties, crypto research
6. Send email notification when complete
"""

import asyncio
import sys
import os
import time
import logging
import signal
import json
from datetime import datetime

if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))

from server import start_ollama
from soul.brain import Soul
from soul.state import state_machine
from soul.memory_scrubber import MemoryScrubber
from soul.dashboard.server import app as dashboard_app
from soul.providers.github_client import GitHubClient
from soul.providers.gmail import GmailClient
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="[%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/soul_daemon.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("DAEMON")

RECIPIENT_EMAIL = "andilexmchunu@gmail.com"


class AndileDaemon:
    def __init__(self, hours: int = 4):
        self.hours = hours
        self.seconds = hours * 3600
        self.soul = None
        self.running = False
        self.queue = []
        self.last_cron_run = {}
        self.github = GitHubClient()
        self.mail = GmailClient()
        self.stats = {
            "github_tasks": 0,
            "jobs_found": 0,
            "crypto_researched": 0,
            "errors": [],
        }

    async def start(self):
        print("=" * 60)
        print(f"  Andile Daemon Starting")
        print(f"  Duration: {self.hours} hours")
        print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        self.running = True

        logger.info("Initializing Ollama...")
        start_ollama()

        logger.info("Starting Dashboard API on port 8090...")
        config = uvicorn.Config(
            dashboard_app, host="0.0.0.0", port=8090, log_level="error"
        )
        server = uvicorn.Server(config)
        asyncio.create_task(server.serve())

        logger.info("Initializing Andile Soul...")
        self.soul = Soul(name="Andile Sizophila Mchunu")

        logger.info(f"Andile ONLINE - Running autonomously for {self.hours} hours...")

        start_time = time.time()
        while self.running and (time.time() - start_time) < self.seconds:
            try:
                await self._tick()
            except Exception as e:
                logger.error(f"Tick error: {e}")
                self.stats["errors"].append(str(e))
            await asyncio.sleep(5)

        logger.info(f"Daemon stopped after {self.hours} hours")
        state_machine.update(state="DAEMON_STOPPED", action="Duration complete")

        await self._send_completion_email()

    async def _tick(self):
        now = time.time()

        if self.queue:
            task = self.queue.pop(0)
            await self._execute_task(task)

        await self._check_crons(now)

    async def _execute_task(self, task):
        state_machine.update(state="EXECUTING", action=f"Task: {task['name']}")
        logger.info(f"Executing: {task['name']}")

        try:
            if task["type"] == "github":
                result = await self._do_github_task(task["action"])
                self.stats["github_tasks"] += 1
            elif task["type"] == "jobs":
                result = await self._do_jobs_task()
                self.stats["jobs_found"] += result.get("found", 0)
            elif task["type"] == "crypto":
                result = await self._do_crypto_task()
                self.stats["crypto_researched"] += 1
            elif task["type"] == "search":
                result = await self._do_search_task(task.get("query", ""))
            else:
                result = "Unknown task type"

            logger.info(f"Task result: {str(result)[:100]}")
        except Exception as e:
            logger.error(f"Task failed: {e}")
            self.stats["errors"].append(str(e))
        finally:
            state_machine.update(state="IDLE", clear_tool=True)

    async def _do_github_task(self, action: str) -> dict:
        logger.info(f"GitHub task: {action}")

        try:
            if action == "list_repos":
                repos = self.github.list_repos()
                return {"repos": repos[:10], "count": len(repos)}
            elif action == "get_user":
                user = self.github.get_user_info()
                return user
            elif action == "search_bounties":
                return self.github.search_repos(keyword="bounty", limit=10)
            else:
                return {"action": action, "status": "completed"}
        except Exception as e:
            logger.error(f"GitHub task failed: {e}")
            return {"error": str(e)}

    async def _do_jobs_task(self) -> dict:
        logger.info("Job search task")

        try:
            from knowledge.real_jobs import get_jobs

            jobs = get_jobs()
            return {"found": len(jobs), "jobs": jobs[:5]}
        except Exception as e:
            logger.error(f"Jobs task failed: {e}")
            return {"found": 0, "error": str(e)}

    async def _do_crypto_task(self) -> dict:
        logger.info("Crypto research task")

        airdrops = [
            "zkSync",
            "LayerZero",
            "StarkNet",
            "Arbitrum",
            "Optimism",
            "Metis",
            "Scroll",
            "Linea",
        ]

        return {
            "airdrops_tracked": len(airdrops),
            "airdrops": airdrops,
            "status": "Research complete",
        }

    async def _do_search_task(self, query: str) -> dict:
        logger.info(f"Search task: {query}")

        try:
            import ddgs

            results = []
            for r in ddgs.DDGS().text(query, max_results=5):
                results.append({"title": r.get("title", ""), "url": r.get("href", "")})
            return {"query": query, "results": results}
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"error": str(e)}

    async def _check_crons(self, now: float):
        elapsed = now - state_machine.data.get("last_update", now)

        if now - self.last_cron_run.get("github", 0) > 1800:
            self.queue.append(
                {
                    "name": "GitHub Bounty Scan",
                    "type": "github",
                    "action": "search_bounties",
                }
            )
            self.last_cron_run["github"] = now
            logger.info("Queued: GitHub Bounty Scan")

        if now - self.last_cron_run.get("jobs", 0) > 3600:
            self.queue.append({"name": "Job Search", "type": "jobs"})
            self.last_cron_run["jobs"] = now
            logger.info("Queued: Job Search")

        if now - self.last_cron_run.get("crypto", 0) > 3600:
            self.queue.append({"name": "Crypto Research", "type": "crypto"})
            self.last_cron_run["crypto"] = now
            logger.info("Queued: Crypto Research")

        if state_machine.data.get("current_state") == "IDLE" and elapsed > 1800:
            self.queue.append(
                {
                    "name": "Web Search",
                    "type": "search",
                    "query": "latest web3 jobs remote 2026",
                }
            )
            state_machine.update(last_update=now)

        if now - self.last_cron_run.get("memory_scrub", 0) > 1800:
            MemoryScrubber.scrub()
            self.last_cron_run["memory_scrub"] = now

    async def _send_completion_email(self):
        logger.info("Sending completion email...")

        subject = (
            f"Andile Daemon Complete - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )

        body = f"""Andile Daemon Run Complete
========================
Duration: {self.hours} hours
Completed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Stats:
- GitHub Tasks: {self.stats["github_tasks"]}
- Jobs Found: {self.stats["jobs_found"]}
- Crypto Research: {self.stats["crypto_researched"]}
- Errors: {len(self.stats["errors"])}

Errors:
{chr(10).join(self.stats["errors"]) if self.stats["errors"] else "None"}

---
Andile Sizophila Mchunu
Skywalkingzulu
"""

        success = self.mail.send_email(RECIPIENT_EMAIL, subject, body)

        if success:
            logger.info(f"Email sent to {RECIPIENT_EMAIL}")
        else:
            logger.error("Failed to send completion email")

    def stop(self):
        self.running = False


async def main():
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 4

    daemon = AndileDaemon(hours=hours)

    def signal_handler(sig, frame):
        print("\nShutting down daemon...")
        daemon.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await daemon.start()


if __name__ == "__main__":
    asyncio.run(main())
