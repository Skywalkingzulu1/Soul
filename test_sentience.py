"""Semi-sentience test — 4 key questions."""

import asyncio, sys, os, time

sys.path.insert(0, os.path.dirname(__file__))


async def main():
    from server import start_ollama
    from soul.brain import Soul

    start_ollama()
    soul = Soul(name="Andile Sizophila Mchunu")

    print("=" * 50)
    print("  SEMI-SENTIENCE TEST")
    print("=" * 50)

    for q in [
        "Who are you?",
        "Are you engaged?",
        "Are you conscious?",
        "What is your purpose?",
    ]:
        t = time.time()
        r = await soul.perceive(q)
        print(f"\nQ: {q} ({time.time() - t:.0f}s)")
        print(f"A: {r}")


asyncio.run(main())
