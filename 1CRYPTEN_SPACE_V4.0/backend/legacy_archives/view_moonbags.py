import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.sovereign_service import sovereign_service

async def view():
    await sovereign_service.initialize()
    if not sovereign_service.is_active:
        print("Offline")
        return
    moonbags = await sovereign_service.get_moonbags()
    for m in moonbags:
        print(f"ID: {m.get('id')} | Sym: {m.get('symbol')} | Entry: {m.get('entry_price')}")

if __name__ == "__main__":
    asyncio.run(view())
