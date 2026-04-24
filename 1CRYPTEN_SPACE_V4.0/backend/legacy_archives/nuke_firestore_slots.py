import asyncio
import os
import sys

# Add backend to path to import services
sys.path.append(os.getcwd())

from services.sovereign_service import sovereign_service

async def nuke():
    print("--- NUKE FIRESTORE SLOTS ---")
    await sovereign_service.initialize()
    await sovereign_service.initialize_db()
    
    slots = await sovereign_service.get_active_slots(force_refresh=True)
    for s in slots:
        slot_id = s.get("id")
        symbol = s.get("symbol")
        if symbol:
            print(f"Cleaning Slot {slot_id} with symbol {symbol}...")
            await sovereign_service.free_slot(slot_id, "FINAL NUKE - Almirante Command")
        else:
            print(f"Slot {slot_id} is already empty.")
    
    print("NUKE COMPLETE. Dashboard should be clean.")

if __name__ == "__main__":
    asyncio.run(nuke())
