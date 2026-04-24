import asyncio
import os
import sys

# Add backend to path to import services
sys.path.append(os.getcwd())

from services.firebase_service import firebase_service

async def nuke():
    print("--- NUKE FIRESTORE SLOTS ---")
    await firebase_service.initialize()
    await firebase_service.initialize_db()
    
    slots = await firebase_service.get_active_slots(force_refresh=True)
    for s in slots:
        slot_id = s.get("id")
        symbol = s.get("symbol")
        if symbol:
            print(f"Cleaning Slot {slot_id} with symbol {symbol}...")
            await firebase_service.free_slot(slot_id, "FINAL NUKE - Almirante Command")
        else:
            print(f"Slot {slot_id} is already empty.")
    
    print("NUKE COMPLETE. Dashboard should be clean.")

if __name__ == "__main__":
    asyncio.run(nuke())
