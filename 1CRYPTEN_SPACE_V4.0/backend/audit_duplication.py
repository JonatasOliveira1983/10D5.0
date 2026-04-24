import asyncio
import os
import sys

# Add parent dir to sys.path if needed
sys.path.append(os.getcwd())

from services.sovereign_service import sovereign_service
from services.bybit_rest import bybit_rest_service

async def audit():
    print("Initializing Firebase...")
    await sovereign_service.initialize()
    
    print("\n--- FIRESTORE TACTICAL SLOTS ---")
    slots = await sovereign_service.get_active_slots(force_refresh=True)
    for s in slots:
        print(f"Slot {s.get('id')}: {s.get('symbol')} | Status: {s.get('status')} | ROI: {s.get('pnl_percent')}%")
        
    print("\n--- FIRESTORE MOONBAGS (VAULT) ---")
    moonbags = await sovereign_service.get_moonbags()
    for m in moonbags:
        print(f"Moonbag: {m.get('symbol')} | Qty: {m.get('qty')} | ROI: {m.get('pnl_percent')}%")
        
    print("\n--- BYBIT/PAPER MOTOR RAM DISCOVERY ---")
    try:
        # Tenta carregar o estado do motor paper
        await bybit_rest_service._load_paper_state()
        print(f"Paper Positions: {[p.get('symbol') for p in bybit_rest_service.paper_positions]}")
        print(f"Paper Moonbags: {[m.get('symbol') for m in bybit_rest_service.paper_moonbags]}")
    except Exception as e:
        print(f"BybitREST Error: {e}")

if __name__ == "__main__":
    asyncio.run(audit())
