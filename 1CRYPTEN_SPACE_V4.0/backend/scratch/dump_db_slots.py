import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath("c:/Users/spcom/Desktop/10D REAL 4.0/1CRYPTEN_SPACE_V4.0/backend"))

from services.database_service import database_service

async def dump():
    await database_service.initialize()
    async with database_service.AsyncSessionLocal() as session:
        from sqlalchemy import select
        from services.database_service import Slot
        result = await session.execute(select(Slot).order_by(Slot.id))
        slots = result.scalars().all()
        print(f"--- DATABASE SLOTS DUMP ---")
        for s in slots:
            print(f"Slot {s.id}: Symbol={s.symbol} | Status={s.status} | GenesisID={s.genesis_id}")

if __name__ == "__main__":
    # Ensure we use the local DB for this audit
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///c:/Users/spcom/Desktop/10D REAL 4.0/1CRYPTEN_SPACE_V4.0/backend/local_sniper.db"
    asyncio.run(dump())
