# EMERGENCY SLOT RESET - V110.193
import asyncio
import os
import sys

# Adiciona o diretório backend ao path
sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))

from services.database_service import database_service
from services.sovereign_service import sovereign_service
from sqlalchemy import text

async def reset_everything():
    print("🚀 Starting Emergency Slot Reset...")
    
    # 1. Initialize DB
    await database_service.initialize()
    
    # 2. Force status_risco = 'LIVRE' and clear symbol in database
    async with database_service.SessionLocal() as session:
        try:
            # PostgreSQL syntax for Railway
            await session.execute(text("UPDATE slots SET status_risco = 'LIVRE', symbol = NULL, side = NULL, entry_price = 0, current_stop = 0, pnl_percent = 0, genesis_id = NULL"))
            # Clear banca status to ensure 4 available
            await session.execute(text("UPDATE banca_status SET slots_disponiveis = 4, status = 'ACTIVE'"))
            await session.commit()
            print("✅ Database slots wiped and set to LIVRE.")
        except Exception as e:
            print(f"❌ Error updating DB: {e}")
            await session.rollback()

    # 3. Sync with Sovereign Service cache
    # Initialize sovereign
    await sovereign_service.initialize()
    # Reset internal slots_cache
    sovereign_service.slots_cache = [{"id": i, "symbol": None, "entry_price": 0, "current_stop": 0, "status_risco": "LIVRE", "pnl_percent": 0} for i in range(1, 5)]
    print("✅ SovereignService cache reset.")

    print("\n🏁 RESET COMPLETE. Captain should now see 0/4 slots occupied.")

if __name__ == "__main__":
    asyncio.run(reset_everything())
