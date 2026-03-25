
import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from soul.brain import Soul

async def test_tools():
    from server import start_ollama
    start_ollama()
    logging.basicConfig(level=logging.INFO)
    soul = Soul()
    
    print("\n" + "="*50)
    print("  TOOL EXECUTION TEST")
    print("="*50)

    # Test 1: Search (Current events)
    q1 = "What is the current price of Bitcoin?"
    print(f"\nTask: {q1}")
    r1 = await soul.perceive(q1)
    print(f"Result: {r1}")

    # Test 2: Code (Calculation)
    q2 = "Calculate the 20th Fibonacci number using Python."
    print(f"\nTask: {q2}")
    r2 = await soul.perceive(q2)
    print(f"Result: {r2}")

    # Test 3: Complex Decompose (Planning)
    q3 = "Research the latest news on Ethereum and summarize it in 3 bullet points."
    print(f"\nTask: {q3}")
    r3 = await soul.perceive(q3)
    print(f"Result: {r3}")

if __name__ == "__main__":
    asyncio.run(test_tools())
