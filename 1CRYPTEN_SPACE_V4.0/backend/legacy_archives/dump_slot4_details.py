
import asyncio
from services.sovereign_service import sovereign_service
import json

async def dump_slot_4():
    await sovereign_service.initialize()
    slot = await sovereign_service.get_slot(4)
    print(json.dumps(slot, indent=2))

if __name__ == "__main__":
    asyncio.run(dump_slot_4())
