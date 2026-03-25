import sys
import os
import asyncio
import ollama

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from soul.brain import Soul
from soul.thinker import ThinkerEngine

async def test_twin_response():
    soul = Soul(name="Andile Sizophila Mchunu")
    question = "what have you done today?"
    
    # 1. Get context (verified in previous test)
    context = soul._get_context(question)
    
    # 2. Get response from thinker
    thinker = ThinkerEngine(name="Andile")
    response = thinker.twin_think(question, context=context)
    
    print("--- AI RESPONSE FOR 'WHAT HAVE YOU DONE TODAY?' ---")
    print(response)

if __name__ == "__main__":
    asyncio.run(test_twin_response())
