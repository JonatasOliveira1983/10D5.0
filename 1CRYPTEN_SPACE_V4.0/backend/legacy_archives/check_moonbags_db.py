
import asyncio
import os
from services.sovereign_service import sovereign_service

async def check():
    await sovereign_service.initialize()
    moonbags = await sovereign_service.get_moonbags()
    print(f"FOUND_MOONBAGS: {len(moonbags)}")
    for m in moonbags:
        print(f"- {m.get('symbol')} | Promoted At: {m.get('promoted_at')}")

if __name__ == "__main__":
    asyncio.run(check())
