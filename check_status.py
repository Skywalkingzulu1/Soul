import asyncio
from soul.brain import Soul

async def main():
    soul = Soul(name="Andile Sizophila Mchunu")
    print(soul.status())

if __name__ == "__main__":
    asyncio.run(main())
