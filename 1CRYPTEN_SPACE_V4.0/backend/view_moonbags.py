import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.firebase_service import firebase_service

async def view():
    await firebase_service.initialize()
    if not firebase_service.is_active:
        print("Offline")
        return
    moonbags = await firebase_service.get_moonbags()
    for m in moonbags:
        print(f"ID: {m.get('id')} | Sym: {m.get('symbol')} | Entry: {m.get('entry_price')}")

if __name__ == "__main__":
    asyncio.run(view())
