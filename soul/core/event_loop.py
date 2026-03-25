import asyncio
from soul.core.logger import setup_logger
from soul.core.config import identity

logger = setup_logger(__name__)

# Maximum queue size to prevent memory exhaustion
MAX_QUEUE_SIZE = 100
# Maximum concurrent tasks
MAX_CONCURRENT_TASKS = 5


class Task:
    def __init__(self, name, priority, func, *args, **kwargs):
        self.name = name
        self.priority = priority
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __lt__(self, other):
        return self.priority < other.priority


class EventLoop:
    """The 'Never Idle' Heartbeat of Soul."""

    def __init__(self):
        # Bounded queue to prevent memory exhaustion
        self.queue = asyncio.PriorityQueue(maxsize=MAX_QUEUE_SIZE)
        self.running = False
        self.current_task = None
        self.active_tasks = 0
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
        self._background_tasks = []

    async def add_task(self, name, priority, func, *args, **kwargs):
        # Check queue capacity
        if self.queue.full():
            logger.warning(f"Task queue full, dropping task: {name}")
            return False

        # PriorityQueue sorts low to high (0 is highest priority)
        await self.queue.put((priority, Task(name, priority, func, *args, **kwargs)))
        logger.info(f"Task added to queue: {name} (Priority: {priority})")
        return True

    async def start(self):
        self.running = True
        logger.info("Soul Event Loop started.")

        # Start background task injector
        self._background_tasks.append(asyncio.create_task(self._background_injector()))

        while self.running:
            if self.queue.empty():
                # Restless Background: Inject maintenance tasks if queue is empty
                await self._inject_background_tasks()

            try:
                # Wait for task with timeout to allow checking running flag
                priority, task = await asyncio.wait_for(self.queue.get(), timeout=5.0)
            except asyncio.TimeoutError:
                continue

            self.current_task = task

            logger.info(f"Executing Task: {task.name}")
            try:
                # Use semaphore to limit concurrent tasks
                async with self.semaphore:
                    self.active_tasks += 1
                    try:
                        if asyncio.iscoroutinefunction(task.func):
                            await task.func(*task.args, **task.kwargs)
                        else:
                            task.func(*task.args, **task.kwargs)
                    finally:
                        self.active_tasks -= 1

            except Exception as e:
                logger.error(f"Task {task.name} failed: {e}")
            finally:
                self.queue.task_done()
                self.current_task = None

            await asyncio.sleep(0.1)

    async def _background_injector(self):
        """Background task to inject maintenance when queue is low."""
        while self.running:
            await asyncio.sleep(60)  # Check every minute
            if self.running and self.queue.qsize() < 3:
                logger.info("Queue running low, preparing background tasks...")
                await self._inject_background_tasks()

    async def _inject_background_tasks(self):
        """When idle, perform reconnaissance or maintenance."""
        # This is where we'd add 'restless' behaviors
        # For now, just a tiny sleep to prevent spinlock
        await asyncio.sleep(5)
        logger.debug("System idle. Running background reconnaissance...")

    def stop(self):
        self.running = False
        # Cancel background tasks
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
        logger.info("Soul Event Loop stopping.")

    def get_status(self):
        """Get current status of the event loop."""
        return {
            "running": self.running,
            "queue_size": self.queue.qsize(),
            "queue_max": MAX_QUEUE_SIZE,
            "active_tasks": self.active_tasks,
            "max_concurrent": MAX_CONCURRENT_TASKS,
            "current_task": self.current_task.name if self.current_task else None,
        }
