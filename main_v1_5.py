import asyncio
import signal
from soul.core.event_loop import EventLoop
from soul.core.resiliency import ResiliencyEngine
from soul.core.memory_manager import MemoryManager
from soul.core.logger import setup_logger
from soul.dashboard.server import app
import uvicorn

logger = setup_logger(__name__)

class SoulV15:
    """The unified V1.5 autonomous engine."""
    
    def __init__(self):
        self.loop = EventLoop()
        self.resiliency = ResiliencyEngine()
        self.memory = MemoryManager()
        self.stop_event = asyncio.Event()

    async def run(self):
        logger.info("Initializing Soul V1.5 Framework...")
        
        # 1. Clean environment
        self.resiliency.kill_zombie_browsers()
        
        # 2. Start Dashboard in background
        config = uvicorn.Config(app, host="0.0.0.0", port=8090, log_level="error")
        server = uvicorn.Server(config)
        asyncio.create_task(server.serve())
        
        # 3. Start the Event Loop
        logger.info("Soul V1.5 is now ONLINE and ready for commands.")
        await self.loop.start()

async def main():
    soul = SoulV15()
    
    # Simple signal handler for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: soul.loop.stop())

    await soul.run()

if __name__ == "__main__":
    asyncio.run(main())
