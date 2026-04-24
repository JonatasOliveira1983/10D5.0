
import asyncio
from services.firebase_service import firebase_service
import json

async def dump_slot_4():
    await firebase_service.initialize()
    slot = await firebase_service.get_slot(4)
    print(json.dumps(slot, indent=2))

if __name__ == "__main__":
    asyncio.run(dump_slot_4())
