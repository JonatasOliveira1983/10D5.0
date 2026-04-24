
import asyncio
import os
import sys

sys.path.append(os.getcwd())
from services.sovereign_service import sovereign_service

async def check():
    await sovereign_service.initialize()
    docs = sovereign_service.db.collection("trade_history").limit(1).get()
    if docs:
        print(f"Schema: {docs[0].to_dict().keys()}")
        print(f"Full: {docs[0].to_dict()}")
    else:
        print("No trades found")

if __name__ == "__main__":
    asyncio.run(check())
