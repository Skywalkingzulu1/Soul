import asyncio
import os
import sys
import logging
import time
import json
from soul.brain import Soul
from soul.tools import WebSearchTool

# Configure logging for 10-hour background mission
logging.basicConfig(
    filename='knowledge/github_bounty_mission.log',
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BOUNTY_HUNTER")

class BugBountyHunter:
    """Specialized mission module for 10-hour deep research/scan."""
    
    def __init__(self, soul):
        self.soul = soul
        self.search = WebSearchTool()
        self.findings = []
        self.start_time = time.time()
        self.duration = 10 * 3600 # 10 hours

    async def run(self):
        logger.info("Starting 10-hour HUMAN-CENTRIC GitHub Bug Bounty Mission... 🚀")
        
        # Phase 1: Deep Surface Recon (Engineering Blogs/Changelogs)
        await self.recon_fresh_surfaces()
        
        # Main Research Loop
        while time.time() - self.start_time < self.duration:
            try:
                # Cycle through complex, non-generic targets
                await self.research_vulnerability_class("Race Conditions in GitHub Actions Runners")
                await asyncio.sleep(1200) 
                
                await self.research_vulnerability_class("Cache Poisoning in Dependabot/Actions-Cache")
                await asyncio.sleep(1200)
                
                await self.research_vulnerability_class("Logic Flaws in Copilot PR Suggestions")
                await asyncio.sleep(1200)
                
                await self.research_vulnerability_class("Bypassing Branch Protection via API Edge Cases")
                await asyncio.sleep(1200)

                # Baby-style ingestion
                logger.info("Mission Ingestion: Humanizing and consolidating findings...")
                await self.soul.sleep(30)
                
            except Exception as e:
                logger.error(f"Mission error: {e}")
                await asyncio.sleep(600)

        # Final Human-Readable Log Generation
        self.generate_human_log()

    async def recon_fresh_surfaces(self):
        logger.info("Reconnaissance: Searching for undocumented features and recent changelogs...")
        query = "site:github.blog 'changelog' OR 'introducing' OR 'beta' 2025 2026"
        res = self.search.execute(query)
        with open("knowledge/fresh_surfaces.txt", "w") as f:
            f.write(res)
        logger.info("Fresh surfaces documented.")

    async def research_vulnerability_class(self, v_class):
        logger.info(f"Human-Thinking Phase: {v_class}")
        query = f"GitHub vulnerability research {v_class} novel techniques -hackerone -bugcrowd"
        res = self.search.execute(query)
        
        # Sophisticated Human-Centric Prompt
        human_prompt = (
            f"You are a Senior Security Researcher at Azania Neptune Labs. "
            f"Think critically about this specific surface: {v_class}. "
            f"Based on these search results: {res}, "
            "write a narrative log entry. Focus on novel, undocumented logic flaws. "
            "Avoid duplicates or low-hanging fruit. Speak in first-person ('I noticed...', 'My intuition suggests...'). "
            "Explain exactly HOW an airtight exploit would work in a real-world scenario."
        )
        
        thought = self.soul.thinker.direct(human_prompt)
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target": v_class,
            "research_data": res[:300],
            "human_analysis": thought
        }
        self.findings.append(entry)
        
        # QUALITY CHECK: Append to a live preview file
        with open("knowledge/LIVE_RESEARCH_PREVIEW.md", "a") as f:
            f.write(f"### [LIVE PREVIEW] Target: {v_class}\n")
            f.write(f"**Timestamp:** {entry['timestamp']}\n\n")
            f.write(entry['human_analysis'])
            f.write("\n\n---\n\n")
            
        logger.info(f"Human log entry completed for {v_class}")

    def generate_human_log(self):
        log_path = "knowledge/SECURITY_RESEARCH_LOG.md"
        with open(log_path, "w") as f:
            f.write("# ANDILE'S SECURITY RESEARCH LOG: GITHUB BOUNTY MISSION\n")
            f.write(f"**Date:** {time.strftime('%Y-%m-%d')}\n")
            f.write("**Author:** Andile Sizophila Mchunu (Skywalkingzulu1)\n\n")
            f.write("## Mission Objective\n")
            f.write("Identify airtight, novel, and non-duplicate logic flaws in GitHub's core infrastructure.\n\n")
            
            for entry in self.findings:
                f.write(f"## Target Analysis: {entry['target']}\n")
                f.write(f"**Timestamp:** {entry['timestamp']}\n\n")
                f.write(entry['human_analysis'])
                f.write("\n\n---\n\n")
                
        logger.info(f"Mission complete. Human-readable log saved to {log_path}")

async def main():
    soul = Soul(name="Andile Sizophila Mchunu")
    hunter = BugBountyHunter(soul)
    await hunter.run()

if __name__ == "__main__":
    asyncio.run(main())
