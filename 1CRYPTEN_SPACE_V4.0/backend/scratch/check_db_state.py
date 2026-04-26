
import asyncio
import os
import sys
sys.path.append(os.getcwd())
from services.database_service import database_service

async def check():
    status = await database_service.get_banca_status()
    print(f"BANCA: ${status.get('saldo_total')}")
    
    history = await database_service.get_trade_history(limit=5)
    print(f"HISTORY COUNT: {len(history)}")
    for t in history:
        print(f" - {t.get('symbol')}: {t.get('pnl')}")

if __name__ == "__main__":
    asyncio.run(check())
