import sys
import os
import asyncio

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from soul.brain import Soul

async def test_context():
    soul = Soul(name="Andile Sizophila Mchunu")
    question = "what have you done today?"
    context = soul._get_context(question)
    print("--- CONTEXT FOR ACTIVITY QUESTION ---")
    print(context)
    
    # Try a normal question
    print("\n--- CONTEXT FOR NORMAL QUESTION ---")
    print(soul._get_context("Who are you?"))

if __name__ == "__main__":
    asyncio.run(test_context())
