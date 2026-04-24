import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath("c:/Users/spcom/Desktop/10D REAL 4.0/1CRYPTEN_SPACE_V4.0/backend"))

from services.sovereign_service import sovereign_service
from services.bybit_rest import bybit_rest_service

async def audit():
    print(f"Execution Mode: {bybit_rest_service.execution_mode}")
    print(f"Paper Positions: {bybit_rest_service.paper_positions}")
    
    slots = await sovereign_service.get_active_slots()
    print(f"Sovereign Slots: {len(slots)}")
    for s in slots:
        print(f"Slot {s.get('id')}: {s.get('symbol')} | {s.get('status_risco')}")

if __name__ == "__main__":
    asyncio.run(audit())
