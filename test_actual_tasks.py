import asyncio
import sys
import os
import logging
from soul.brain import Soul
from server import start_ollama

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ActualTasksTest")

async def run_task(num, description, coro_func, *args, **kwargs):
    print(f"\n[Task {num:2}/10] Starting: {description}")
    try:
        # If it's a coroutine function, call it with args
        if asyncio.iscoroutinefunction(coro_func):
            result = await coro_func(*args, **kwargs)
        else:
            # If it's a regular function or a coroutine object
            res = coro_func(*args, **kwargs)
            if asyncio.iscoroutine(res):
                result = await res
            else:
                result = res
        
        print(f"[Task {num:2}/10] SUCCESS")
        print(f"Result Preview: {str(result)[:200]}...")
        return True, result
    except Exception as e:
        print(f"[Task {num:2}/10] FAILED: {e}")
        return False, str(e)

async def main():
    print("=" * 60)
    print("  SOUL - ACTUAL TASKS TEST SUITE")
    print("=" * 60)

    start_ollama()
    soul = Soul(name="Andile Sizophila Mchunu")
    
    results = []
    
    # 1. Information Retrieval
    results.append(await run_task(1, "Web Search: Latest Ethereum Price", 
        soul.tools.execute, "search", "current price of Ethereum in USD"))

    # 2. Web Analysis
    results.append(await run_task(2, "Browser: Summarize Python.org", 
        soul.perceive, "Go to python.org and tell me what the latest version of Python is."))

    # 3. Code Generation
    results.append(await run_task(3, "Code Gen: Write a Fibonacci function", 
        soul.perceive, "Write a Python function to calculate the Nth Fibonacci number."))

    # 4. Logic Problem
    results.append(await run_task(4, "Logic: Solve a word problem", 
        soul.perceive, "If I have 5 apples and give 2 to Mary, then Mary gives 1 back to me, how many apples do I have? Explain your reasoning."))

    # 5. Philosophy
    results.append(await run_task(5, "Philosophy: Dialectic on AI Ethics", 
        soul.perceive, "/dialectic The ethics of artificial intelligence and human agency"))

    # 6. Memory Recall
    soul.memory.store("secret_key", "The password is 'Ubuntu2026'", importance=1.0)
    results.append(await run_task(6, "Memory: Recall secret key", 
        soul.perceive, "What was that secret password I just told you?"))

    # 7. Planning
    results.append(await run_task(7, "Planning: Trip to Tokyo", 
        soul.perceive, "Plan a 3-day itinerary for a first-time visitor to Tokyo."))

    # 8. Communication
    results.append(await run_task(8, "Communication: Draft Email", 
        soul.perceive, "Draft a professional email to a project manager explaining that the DeFi dashboard will be delayed by two days due to API integration issues."))

    # 9. Self-Reflection
    results.append(await run_task(9, "Reflection: Analyze performance", 
        soul.reflect_on_last))

    # 10. System Status
    results.append(await run_task(10, "Status: Full system report", 
        soul.status))

    passed = sum(1 for r in results if r[0])
    print(f"\n{'=' * 60}")
    print(f"  ACTUAL TASKS FINAL REPORT")
    print(f"{'=' * 60}")
    print(f"  Passed: {passed}/10")
    print(f"  Grade: {'A' if passed >= 9 else 'B' if passed >= 8 else 'C' if passed >= 7 else 'F'}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    asyncio.run(main())
