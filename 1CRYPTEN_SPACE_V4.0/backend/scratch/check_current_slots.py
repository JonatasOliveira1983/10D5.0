import asyncio
import os
import sys

# Adicionar o diretório atual ao path para importar os serviços
sys.path.append(os.getcwd())

from services.database_service import database_service

async def check_slots():
    try:
        slots = await database_service.get_active_slots()
        print("\n=== STATUS DOS SLOTS NO POSTGRES ===")
        for s in slots:
            sym = s.get('symbol')
            if sym:
                print(f"Slot {s['id']}: {sym} | {s.get('side')} | PnL: {s.get('pnl_percent')}% | Genesis: {s.get('genesis_id')}")
            else:
                print(f"Slot {s['id']}: [LIVRE]")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    asyncio.run(check_slots())
