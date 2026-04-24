
import asyncio
import os
import sys

sys.path.append(os.getcwd())
from services.firebase_service import firebase_service

async def check():
    await firebase_service.initialize()
    doc = firebase_service.db.collection("vault_management").document("current_cycle").get()
    print(f"Firestore current_cycle: {doc.to_dict()}")

if __name__ == "__main__":
    asyncio.run(check())
