import asyncio
import os
import sys

sys.path.append(os.getcwd())

from services.firebase_service import firebase_service

async def cleanup():
    print("[CLEANUP] Starting IPUSDT deduplication...")
    if not firebase_service.is_active:
        await firebase_service.initialize()
    
    # 1. Firestore Cleanup
    moonbags_ref = firebase_service.db.collection("moonbags")
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
    if firebase_service.rtdb:
        # In firebase-admin, .get() returns the dict directly
        rtdb_moons = firebase_service.rtdb.child("moonbags").get()
        if rtdb_moons and isinstance(rtdb_moons, dict):
            for k, v in rtdb_moons.items():
                if v.get("symbol") == "IPUSDT":
                    print(f"Removing RTDB duplicate: IPUSDT")
                    firebase_service.rtdb.child("moonbags").child(k).remove()
                    
    print(f"Cleanup finished. Removed {deleted_docs} duplicates from Firestore.")

if __name__ == "__main__":
    asyncio.run(cleanup())
