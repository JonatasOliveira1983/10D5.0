import asyncio
import os
import json
from services.sovereign_service import sovereign_service

async def kill_ghosts():
    print("Loading firebase...")
    await sovereign_service.initialize()
    
    # 1. Kill 'moonbags' collection
    print("Deleting 'moonbags' collection...")
    docs = await asyncio.to_thread(sovereign_service.db.collection("moonbags").get)
    for doc in docs:
        await asyncio.to_thread(doc.reference.delete)
    
    # 2. Kill 'system_state/paper_engine'
    print("Deleting 'system_state/paper_engine'...")
    await asyncio.to_thread(sovereign_service.db.collection("system_state").document("paper_engine").delete)

    # 3. Kill RTDB 'moonbag_vault'
    print("Deleting RTDB 'moonbag_vault'...")
    await asyncio.to_thread(sovereign_service.rtdb.reference("moonbag_vault").set, {})
    
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
