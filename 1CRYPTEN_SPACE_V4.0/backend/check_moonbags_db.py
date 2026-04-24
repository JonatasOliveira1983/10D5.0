
import asyncio
import os
from services.firebase_service import firebase_service

async def check():
    await firebase_service.initialize()
    moonbags = await firebase_service.get_moonbags()
    print(f"FOUND_MOONBAGS: {len(moonbags)}")
    for m in moonbags:
        print(f"- {m.get('symbol')} | Promoted At: {m.get('promoted_at')}")

if __name__ == "__main__":
    asyncio.run(check())
