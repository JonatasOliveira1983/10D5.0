
import asyncio
from services.sovereign_service import sovereign_service
import json

async def dump_all_slots():
    await sovereign_service.initialize()
    slots = await sovereign_service.get_active_slots()
    print(json.dumps(slots, indent=2))

if __name__ == "__main__":
    asyncio.run(dump_all_slots())
