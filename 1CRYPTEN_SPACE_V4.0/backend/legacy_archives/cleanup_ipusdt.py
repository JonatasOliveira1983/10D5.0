import asyncio
import os
import sys

sys.path.append(os.getcwd())

from services.sovereign_service import sovereign_service

async def cleanup():
    print("[CLEANUP] Starting IPUSDT deduplication...")
    if not sovereign_service.is_active:
        await sovereign_service.initialize()
    
    # 1. Firestore Cleanup
    moonbags_ref = sovereign_service.db.collection("moonbags")
    docs = moonbags_ref.stream()
    deleted_docs = 0
    
    for doc in docs:
        data = doc.to_dict()
        sym = data.get("symbol", "")
        # Remove anything that is exactly 'IPUSDT'
        if sym == "IPUSDT":
            print(f"Removing Firestore duplicate: {sym} (ID: {doc.id})")
            doc.reference.delete()
            deleted_docs += 1
            
    # 2. RTDB Cleanup
    if sovereign_service.rtdb:
        # In firebase-admin, .get() returns the dict directly
        rtdb_moons = sovereign_service.rtdb.child("moonbags").get()
        if rtdb_moons and isinstance(rtdb_moons, dict):
            for k, v in rtdb_moons.items():
                if v.get("symbol") == "IPUSDT":
                    print(f"Removing RTDB duplicate: IPUSDT")
                    sovereign_service.rtdb.child("moonbags").child(k).remove()
                    
    print(f"Cleanup finished. Removed {deleted_docs} duplicates from Firestore.")

if __name__ == "__main__":
    asyncio.run(cleanup())
