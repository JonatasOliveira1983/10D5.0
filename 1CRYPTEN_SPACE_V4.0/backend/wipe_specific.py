import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.firebase_service import firebase_service

async def wipe_specific():
    await firebase_service.initialize()
    if not firebase_service.is_active:
        print("Firebase FAIL")
        return
    
    print("🔥 WIPING SLOT 4...")
    res4 = await firebase_service.free_slot(4, reason="MANUAL WIPE")
    print(f"RESULT 4: {res4}")
    
    print("🔥 WIPING SLOT 2...")
    res2 = await firebase_service.free_slot(2, reason="MANUAL WIPE")
    print(f"RESULT 2: {res2}")
    
    if firebase_service.rtdb:
         firebase_service.rtdb.child("live_slots").child("4").delete()
         firebase_service.rtdb.child("live_slots").child("2").delete()
         print("RTDB WIPE DONE")

if __name__ == "__main__":
    asyncio.run(wipe_specific())
