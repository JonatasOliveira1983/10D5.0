import asyncio
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_service import database_service

async def check_local_db():
    print("Checking Local PostgreSQL database...")
    try:
        await database_service.initialize()
        slots = await database_service.get_active_slots()
        print("\n--- LOCAL POSTGRES SLOTS ---")
        for s in slots:
            print(f"Slot {s['id']}: {s.get('symbol')} | Status: {s.get('status_risco')} | Entry: {s.get('entry_price')}")
            
        banca = await database_service.get_banca_status()
        print("\n--- BANCA STATUS ---")
        print(json.dumps(banca, indent=2, default=str))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_local_db())
