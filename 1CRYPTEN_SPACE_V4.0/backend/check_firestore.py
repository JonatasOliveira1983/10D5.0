
import asyncio
import os
import sys

sys.path.append(os.getcwd())
from services.sovereign_service import sovereign_service

async def check():
    await sovereign_service.initialize()
    doc = sovereign_service.db.collection("vault_management").document("current_cycle").get()
    print(f"Firestore current_cycle: {doc.to_dict()}")

if __name__ == "__main__":
    asyncio.run(check())
