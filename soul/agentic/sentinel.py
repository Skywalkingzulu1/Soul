"""The Sentinel Master Agent - 24/7 Autonomous Coordinator.

Coordinates the Guardian, BountyHunter, and Outreach modules
to ensure your digital presence is always growing and profitable.
"""

import asyncio
import logging
import requests
from soul.agentic.guardian import RepoGuardian
from soul.agentic.bounty_hunter import BountyHunter
from soul.agentic.outreach import OutreachAgent
from soul.agentic.state_manager import StateManager

logger = logging.getLogger(__name__)

class Sentinel:
    def __init__(self, soul):
        self.soul = soul
        self.guardian = RepoGuardian(soul)
        self.hunter = BountyHunter(soul)
        self.outreach = OutreachAgent(soul)
        self.state = StateManager()

    async def autonomous_cycle(self, hourly_mode=True):
        """The core 24/7 'Sentinel' loop (The Pulse Protocol)."""
        while True:
            logger.info("\n" + "🚀" * 30)
            logger.info("   SENTINEL: STARTING PULSE PROTOCOL")
            logger.info("🚀" * 30 + "\n")

            try:
                # PHASE 1: RECON
                self.state.update_status("🔍 Phase 1: Recon", "Syncing state and fetching repos")
                
                batch = self.state.get_next_repos(count=3)
                if not batch: # Queue empty, refill
                    logger.info("🛡️ Sentinel: Refilling repo queue from GitHub profile...")
                    headers = {"Authorization": f"token {self.guardian.github_token}"}
                    response = requests.get(f"https://api.github.com/users/{self.guardian.username}/repos", headers=headers)
                    if response.status_code == 200:
                        repos = [r['name'] for r in response.json() if not r['fork']]
                        self.state.refill_queue(repos)
                        batch = self.state.get_next_repos(count=3)

                # PHASE 2: FORTRESS (Guardian)
                for repo_name in batch:
                    self.state.update_status("🛡️ Phase 2: Fortress", f"Perfecting {repo_name}")
                    await self.guardian.perfect_repo(repo_name)
                    self.state.increment_stat("prs_made")

                # PHASE 3: HUNTER (Bounty)
                self.state.update_status("💰 Phase 3: Hunter", "Scanning DeFi protocols for bounties")
                await self.hunter.hunt()
                # If a bounty was found, we'd increment stats here

                # PHASE 4: AGENT (Outreach)
                self.state.update_status("💼 Phase 4: Agent", "Outreach & Job Applications")
                await self.outreach.scan_for_clients()
                
                # Apply to jobs
                app_result = await self.outreach.apply_to_jobs()
                self.state.increment_stat("jobs_applied")
                self.state.increment_stat("emails_sent")

                # PHASE 5: REPORTING
                self.state.update_status("✅ Phase 5: Complete", "Pulse finished successfully")
                self.state.save()

                if hourly_mode:
                    logger.info("✅ SENTINEL: HOURLY PULSE COMPLETE. EXITING...")
                    return 
                
                logger.info("✅ SENTINEL: CYCLE COMPLETE. SLEEPING...")
                await asyncio.sleep(4 * 3600)

            except Exception as e:
                logger.error(f"❌ SENTINEL CRITICAL ERROR: {e}")
                self.state.update_status("❌ Error", str(e))
                await asyncio.sleep(300)
