import asyncio
import os
from services.sovereign_service import sovereign_service
from config import settings

async def check_active_slots():
    await sovereign_service.initialize()
    # [V110.25.0] get_active_slots now returns a list of dictionaries
    slots = await sovereign_service.get_active_slots()
    print("--- SLOTS ATIVOS ---")
    for data in slots:
        if data.get("symbol"):
            print(f"Slot {data.get('id')}: {data['symbol']} | Side: {data.get('side')} | Conf: {data.get('unified_confidence')}%")
            print(f"Whale: {data.get('fleet_intel', {}).get('micro')}% | SMC: {data.get('fleet_intel', {}).get('smc')}%")
            print(f"Entry: {data.get('entry_price')} | SL: {data.get('current_stop')}")
            print("-" * 20)

if __name__ == "__main__":
    asyncio.run(check_active_slots())
