import asyncio
import os
import json
from services.firebase_service import firebase_service

async def kill_ghosts():
    print("Loading firebase...")
    await firebase_service.initialize()
    
    # 1. Kill 'moonbags' collection
    print("Deleting 'moonbags' collection...")
    docs = await asyncio.to_thread(firebase_service.db.collection("moonbags").get)
    for doc in docs:
        await asyncio.to_thread(doc.reference.delete)
    
    # 2. Kill 'system_state/paper_engine'
    print("Deleting 'system_state/paper_engine'...")
    await asyncio.to_thread(firebase_service.db.collection("system_state").document("paper_engine").delete)

    # 3. Kill RTDB 'moonbag_vault'
    print("Deleting RTDB 'moonbag_vault'...")
    await asyncio.to_thread(firebase_service.rtdb.reference("moonbag_vault").set, {})
    
    # 4. Clean local paper storage just in case
    print("Cleaning local paper_storage.json...")
    paper_path = "paper_storage.json"
    if os.path.exists(paper_path):
        with open(paper_path, 'r') as f:
            data = json.load(f)
        data["moonbags"] = []
        data["positions"] = []
        with open(paper_path, 'w') as f:
            json.dump(data, f)
            
    print("Ghosts have been exterminated.")

if __name__ == "__main__":
    asyncio.run(kill_ghosts())
