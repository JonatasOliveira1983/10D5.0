import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), '1CRYPTEN_SPACE_V4.0', 'backend'))

from services.agents.captain import captain_agent
from services.bybit_rest import bybit_rest_service

async def check_status():
    print(f"--- SYSTEM STATUS ---")
    print(f"Execution Mode: {bybit_rest_service.execution_mode}")
    print(f"Paper Positions: {len(bybit_rest_service.paper_positions)}")
    for pos in bybit_rest_service.paper_positions:
        print(f"  - {pos['symbol']} | Side: {pos['side']} | Slot: {pos.get('slot_id')}")
    
    print(f"\nActive Slots (Memory):")
    for sid, data in captain_agent.active_slots.items():
        print(f"  Slot {sid}: {data}")
    
    print(f"\nActive Tocaias: {captain_agent.active_tocaias}")
    
    print(f"\nIs Slot 1 Available? {captain_agent.active_slots.get(1) is None}")

if __name__ == "__main__":
    asyncio.run(check_status())
