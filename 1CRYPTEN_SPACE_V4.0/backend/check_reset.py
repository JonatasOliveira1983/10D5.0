# check_reset.py
import asyncio
import os
import sys

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from services.database_service import database_service

async def check():
    try:
        await database_service.initialize()
        banca = await database_service.get_banca_status()
        vault = await database_service.get_vault_cycle()
        slots = await database_service.get_active_slots()
        
        print(f"Banca: {banca.get('saldo_total')}")
        print(f"Vault Ciclo: {vault.get('cycle_number') if vault else 'N/A'}")
        print(f"Slots: {len([s for s in slots if s.get('symbol')])} ocupados")
    finally:
        await database_service.engine.dispose()

if __name__ == "__main__":
    asyncio.run(check())
