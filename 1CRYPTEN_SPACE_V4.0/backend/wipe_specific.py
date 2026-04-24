import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sovereign_service import sovereign_service

async def wipe_specific():
    await sovereign_service.initialize()
    if not sovereign_service.is_active:
        print("Firebase FAIL")
        return
    
    print("🔥 WIPING SLOT 4...")
    res4 = await sovereign_service.free_slot(4, reason="MANUAL WIPE")
    print(f"RESULT 4: {res4}")
    
    print("🔥 WIPING SLOT 2...")
    res2 = await sovereign_service.free_slot(2, reason="MANUAL WIPE")
    print(f"RESULT 2: {res2}")
    
    if sovereign_service.rtdb:
         sovereign_service.rtdb.child("live_slots").child("4").delete()
         sovereign_service.rtdb.child("live_slots").child("2").delete()
         print("RTDB WIPE DONE")

if __name__ == "__main__":
    asyncio.run(wipe_specific())
