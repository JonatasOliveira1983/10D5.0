import asyncio
import os
import sys

# Add backend to path to import services
sys.path.append(os.getcwd())

from services.firebase_service import firebase_service

async def nuke_rtdb():
    print("--- NUKE RTDB SLOTS ---")
    await firebase_service.initialize()
    await firebase_service.initialize_db()
    
    if firebase_service.rtdb:
        print("Cleaning live_slots in RTDB...")
        # Clear all 4 slots in RTDB
        for i in range(1, 5):
            firebase_service.rtdb.child("live_slots").child(str(i)).delete()
            print(f"RTDB Slot {i} removed.")
        
        # Also system_pulse/state just in case
        firebase_service.rtdb.child("system_state").update({"status": "CLEAN_BOOT", "occupied_count": 0})
        
    print("RTDB NUKE COMPLETE.")

if __name__ == "__main__":
    asyncio.run(nuke_rtdb())
