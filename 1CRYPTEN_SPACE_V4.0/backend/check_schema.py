
import asyncio
import os
import sys

sys.path.append(os.getcwd())
from services.firebase_service import firebase_service

async def check():
    await firebase_service.initialize()
    docs = firebase_service.db.collection("trade_history").limit(1).get()
    if docs:
        print(f"Schema: {docs[0].to_dict().keys()}")
        print(f"Full: {docs[0].to_dict()}")
    else:
        print("No trades found")

if __name__ == "__main__":
    asyncio.run(check())
