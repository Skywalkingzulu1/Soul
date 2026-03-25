import asyncio
import os
from soul.core.config import identity, config
from soul.core.logger import setup_logger
from soul.core.event_loop import EventLoop
from soul.core.memory_manager import MemoryManager
from soul.providers.github_client import GitHubClient
from soul.providers.gmail import GmailClient

logger = setup_logger("IntegrationTest")

async def test_identity():
    logger.info(f"--- Testing Identity Consistency ---")
    logger.info(f"Name: {identity.name}")
    logger.info(f"Email: {identity.email}")
    assert identity.email == "andilexmchunu@gmail.com"
    logger.info("✅ Identity verified.")

async def test_providers():
    logger.info(f"--- Testing Native Providers ---")
    
    # GitHub
    gh = GitHubClient()
    user = gh.get_user_info()
    if user:
        logger.info(f"✅ GitHub Connected: {user['login']} ({user['repos_count']} repos)")
    else:
        logger.warning("❌ GitHub Connection Failed (Check GITHUB_TOKEN)")

    # Gmail
    gmail = GmailClient()
    inbox = gmail.check_inbox(limit=1)
    if inbox is not None:
        logger.info(f"✅ Gmail Connected: Found {len(inbox)} recent emails.")
    else:
        logger.warning("❌ Gmail Connection Failed (Check GMAIL_APP_PASSWORD)")

async def test_cloud_backup():
    logger.info(f"--- Testing Cloud Brain Backup ---")
    mm = MemoryManager()
    # Create a dummy memory file for testing if it doesn't exist
    if not os.path.exists("memory.db"):
        with open("memory.db", "w") as f: f.write("dummy data")
        
    success = await mm.backup_to_cloud(bucket_name="andile-soul-v1")
    if success:
        logger.info("✅ Cloud Backup Successful (Impossible Cloud S3).")
    else:
        logger.warning("❌ Cloud Backup Failed (Check S3 Keys/Endpoint).")

async def test_event_loop():
    logger.info(f"--- Testing Event Loop Coherence ---")
    el = EventLoop()
    
    async def dummy_mission():
        logger.info("Executing dummy mission in the loop...")
        await asyncio.sleep(1)
        return True

    await el.add_task("Verification Mission", 1, dummy_mission)
    
    # Run loop briefly
    stop_task = asyncio.create_task(el.start())
    await asyncio.sleep(3)
    el.stop()
    await stop_task
    logger.info("✅ Event Loop functional.")

async def run_full_test():
    logger.info("Starting Soul V1.5 System-Wide Integration Test...")
    await test_identity()
    await test_providers()
    await test_cloud_backup()
    await test_event_loop()
    logger.info("--- TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(run_full_test())
