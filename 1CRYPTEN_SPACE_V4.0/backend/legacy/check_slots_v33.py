import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.sovereign_service import sovereign_service

async def run():
    await sovereign_service.initialize()
    slots = await sovereign_service.get_active_slots()
    
    for slot in slots:
        if slot.get("symbol"):
            print(f"--- {slot['symbol']} ---")
            print(f"Entry: {slot.get('entry_price')}")
            print(f"Stop:  {slot.get('current_stop')}")
            print(f"Target: {slot.get('target_price')}")
            print(f"Pensamento: {slot.get('pensamento')}")

if __name__ == "__main__":
    asyncio.run(run())
