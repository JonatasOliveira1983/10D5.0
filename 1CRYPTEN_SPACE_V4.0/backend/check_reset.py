import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from services.database_service import database_service

async def main():
    await database_service.initialize()
    status = await database_service.get_banca_status()
    print(f"BANCA_STATUS: {status}")
    
    slots = await database_service.get_active_slots()
    print(f"SLOTS: {slots}")
    
    history = await database_service.get_trade_history(limit=5)
    print(f"HISTORY_COUNT: {len(history)}")

if __name__ == "__main__":
    asyncio.run(main())
