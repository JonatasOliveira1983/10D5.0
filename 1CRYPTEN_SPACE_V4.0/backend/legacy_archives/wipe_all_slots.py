import asyncio
import os
import sys

sys.path.append(os.getcwd())

from services.sovereign_service import sovereign_service
from services.bybit_rest import bybit_rest_service

async def wipe_slots():
    print("[WIPE] Starting absolute slot purge...")
    if not sovereign_service.is_active:
        await sovereign_service.initialize()
    
    # 1. Clear Tactical Slots in Firestore (1 to 4)
    for i in range(1, 5):
        print(f"Cleaning Firestore Slot {i}...")
        await sovereign_service.hard_reset_slot(i, reason="USER_MANUAL_PURGE")
        
    # 2. Clear Paper Positions in BybitREST Memory (to prevent re-adoption)
    print("Clearing BybitREST Paper Memory...")
    bybit_rest_service.paper_positions = []
    # Force saving clean state
    await bybit_rest_service._save_paper_state()
    
    # 3. Clear RTDB Slots
    if sovereign_service.rtdb:
        print("Cleaning RTDB Slots...")
        for i in range(1, 5):
            sovereign_service.rtdb.child("slots").child(str(i)).update({
                "symbol": None,
                "status_risco": "LIVRE",
                "pnl_percent": 0,
                "entry_price": 0,
                "current_stop": 0,
                "side": None
            })
            
    print("[WIPE] All slots and paper positions cleared successfully.")

if __name__ == "__main__":
    asyncio.run(wipe_slots())
