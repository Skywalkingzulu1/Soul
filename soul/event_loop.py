import asyncio
import logging
import time
from soul.state import state_machine
from soul.brain import Soul
from soul.memory_scrubber import MemoryScrubber

logger = logging.getLogger("EVENT_LOOP")

class AutonomousLoop:
    def __init__(self, soul: Soul) -> None:
        self.soul = soul
        self.queue = []
        self.running = False
        self.last_cron_run = {}

    async def start(self) -> None:
        self.running = True
        logger.info("Autonomous Event Loop Started.")
        state_machine.update(state="IDLE", action="Event Loop Monitoring")
        
        while self.running:
            try:
                await self._tick()
            except Exception as e:
                logger.error(f"Loop error: {e}")
                state_machine.update(state="ERROR", action=f"Loop crash: {e}")
            await asyncio.sleep(5) # Tick every 5 seconds

    async def _tick(self) -> None:
        # 1. Process Queue
        if self.queue:
            task = self.queue.pop(0)
            await self._execute_task(task)
        else:
            # 2. Check Cron Jobs (Only if IDLE and no pending tasks)
            await self._check_crons()

    async def _execute_task(self, task) -> None:
        state_machine.update(state="EXECUTING", action=f"Task: {task['name']}")
        logger.info(f"Executing task: {task['name']}")
        
        try:
            # Execute logic based on task type
            if task['type'] == "tool":
                result = await self.soul.tools.execute(task['tool_name'], *task.get('args', []), **task.get('kwargs', {}))
                self.soul.memory.store("action", f"Background executed {task['tool_name']}. Result: {str(result)[:200]}", importance=0.8)
            elif task['type'] == "thought":
                 response = self.soul.thinker.chain_of_thought(task['query'])
                 self.soul.memory.store("action", f"Background thought: {task['query']}. Result: {response[:200]}", importance=0.6)
                 
        except Exception as e:
            logger.error(f"Task failed: {e}")
        finally:
            state_machine.update(state="IDLE", clear_tool=True)

    async def _check_crons(self) -> None:
        now = time.time()
        
        # Cron 1: Daily Job Hunt (Every 24h)
        if now - self.last_cron_run.get("job_hunt", 0) > 86400:
            self.queue.append({"name": "Daily Fintech Job Scan", "type": "tool", "tool_name": "search", "args": ["latest web3 fintech jobs remote cape town"]})
            self.last_cron_run["job_hunt"] = now
            
        # Cron 2: GitHub Scraper (Every 12h)
        if now - self.last_cron_run.get("github_scan", 0) > 43200:
            self.queue.append({"name": "Scan GitHub Bounties", "type": "tool", "tool_name": "search", "args": ["github open source web3 bounties"]})
            self.last_cron_run["github_scan"] = now

        # Cron 3: Boredom Execution (If idle for > 1 hour)
        if state_machine.data['current_state'] == "IDLE" and (now - state_machine.data.get('last_update', now)) > 3600:
             self.queue.append({"name": "Boredom Research", "type": "thought", "query": "Synthesize recent trends in Zero-Knowledge proofs for DeFi."})

        # Cron 4: Memory Scrubber (Every 1h)
        if now - self.last_cron_run.get("memory_scrub", 0) > 3600:
             MemoryScrubber.scrub()
             self.last_cron_run["memory_scrub"] = now

        # Cron 5: Programmatic SEO App Factory (Every 1h)
        # Target: ~80 apps/hour to hit 1000/day safely within rate limits.
        if now - self.last_cron_run.get("seo_factory", 0) > 3600:
             from soul.app_factory import AppFactory
             self.queue.append({"name": "SEO App Factory Batch", "type": "tool", "tool_name": "shell", "args": ["python -c \"from soul.app_factory import AppFactory; AppFactory().run_batch(80)\""]})
             self.last_cron_run["seo_factory"] = now

    def stop(self) -> None:
        self.running = False
        logger.info("Autonomous Event Loop Stopped.")

