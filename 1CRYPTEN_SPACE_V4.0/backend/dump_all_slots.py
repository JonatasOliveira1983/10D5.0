
import asyncio
from services.firebase_service import firebase_service
import json

async def dump_all_slots():
    await firebase_service.initialize()
    slots = await firebase_service.get_active_slots()
    print(json.dumps(slots, indent=2))

if __name__ == "__main__":
    asyncio.run(dump_all_slots())
