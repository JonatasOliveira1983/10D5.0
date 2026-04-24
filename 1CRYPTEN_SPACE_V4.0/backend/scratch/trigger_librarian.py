import asyncio
from services.agents.librarian import librarian_agent
from services.kernel.dispatcher import kernel

async def trigger():
    print("Triggering Librarian Study...")
    await librarian_agent.perform_full_market_study()
    print("Study completed!")

if __name__ == "__main__":
    asyncio.run(trigger())
