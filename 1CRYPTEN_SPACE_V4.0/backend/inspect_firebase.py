import asyncio
import os
import sys
import codecs

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend to path to import services
sys.path.append(os.getcwd())

from services.sovereign_service import sovereign_service

async def inspect():
    print("--- FIRESTORE INSPECTION ---")
    await sovereign_service.initialize()
    await sovereign_service.initialize_db()
    
    collections = ["slots_ativos", "live_slots", "slots", "active_positions"]
    
    for coll_name in collections:
        print(f"\nScanning collection: {coll_name}")
        docs = sovereign_service.db.collection(coll_name).stream()
        count = 0
        for doc in docs:
            print(f"  Document [{doc.id}]: {doc.to_dict()}")
            count += 1
        if count == 0:
            print("  (Empty)")

    if sovereign_service.rtdb:
        print("\n--- RTDB INSPECTION ---")
        live_slots = sovereign_service.rtdb.child("live_slots").get()
        print(f"RTDB live_slots: {live_slots}")
        
    print("\nINSPECTION COMPLETE.")

if __name__ == "__main__":
    asyncio.run(inspect())
