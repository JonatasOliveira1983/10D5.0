import asyncio
import os
import sys

sys.path.append(os.getcwd())

from services.firebase_service import firebase_service
from services.bybit_rest import bybit_rest_service

async def check():
    await firebase_service.initialize()
    
    print("\n--- BUSCANDO IPUSDT ---")
    
    # 1. Slots
    slots = await firebase_service.get_active_slots(force_refresh=True)
    for s in slots:
        sym = s.get("symbol")
        if sym and "IPUSDT" in sym.upper():
            print(f"Slot {s['id']}: {sym} | Status: {s.get('status')}")
            
    # 2. Moonbags
    moons = await firebase_service.get_moonbags()
    for m in moons:
        sym = m.get("symbol")
        if sym and "IPUSDT" in sym.upper():
            print(f"Moonbag: {sym} | Qty: {m.get('qty')}")
            
    # 3. Paper Engine
    await bybit_rest_service._load_paper_state()
    for p in bybit_rest_service.paper_positions:
        sym = p.get("symbol")
        if sym and "IPUSDT" in sym.upper():
            print(f"Paper Position: {sym} | Status: {p.get('status')}")
            
    for m in bybit_rest_service.paper_moonbags:
        sym = m.get("symbol")
        if sym and "IPUSDT" in sym.upper():
            print(f"Paper Moonbag: {sym}")

if __name__ == "__main__":
    asyncio.run(check())
