
import asyncio
import os
from services.bybit_rest import BybitREST
from config import settings

async def check_real_positions():
    print(f"--- CHECKING REAL BYBIT POSITIONS ---")
    print(f"API KEY: {settings.BYBIT_API_KEY[:4]}...{settings.BYBIT_API_KEY[-4:]}")
    
    bybit = BybitREST()
    positions = await bybit.get_active_positions()
    
    if not positions:
        print("❌ Nenhuma posição ativa encontrada na Bybit.")
    else:
        print(f"✅ Encontrada(s) {len(positions)} posição(ões):")
        for pos in positions:
            print(f"- {pos.get('symbol')}: {pos.get('size')} @ {pos.get('avgPrice')} (Side: {pos.get('side')})")

if __name__ == "__main__":
    asyncio.run(check_real_positions())
