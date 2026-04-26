import asyncio
import os
from dotenv import load_dotenv
import sys

sys.path.append(os.getcwd())
load_dotenv(".env")

from services.database_service import database_service

async def check_state():
    banca = await database_service.get_banca_status()
    slots = await database_service.get_active_slots()
    history = await database_service.get_trade_history(limit=10)
    
    print(f"Banca: {banca}")
    print(f"Slots Ativos: {len([s for s in slots if s.get('symbol')])}")
    print(f"Histórico Count (recent): {len(history)}")

if __name__ == "__main__":
    asyncio.run(check_state())
