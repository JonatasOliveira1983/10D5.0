import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.getcwd())

# Explicitly load .env
load_dotenv(".env")

from services.database_service import database_service, Slot, TradeHistory, BancaStatus, Moonbag, VaultCycle, SystemState
from sqlalchemy import delete, update, select

async def reset_system():
    print("[RESET-SOVEREIGN] Starting nuclear reset...")
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        print(f"Connection String: {db_url[:20]}...")
    else:
        print("CRITICAL: DATABASE_URL not found in environment!")
        return
    
    async with database_service.AsyncSessionLocal() as session:
        try:
            # 1. Clear Slots
            print("Cleaning slots...")
            await session.execute(update(Slot).values(
                symbol=None, side=None, qty=0.0, entry_price=0.0, entry_margin=0.0,
                current_stop=0.0, initial_stop=0.0, target_price=0.0, liq_price=0.0,
                pnl_percent=0.0, status_risco="LIVRE", order_id=None, genesis_id=None,
                fleet_intel=None, pensamento=None,
                symbol_adx=0.0, market_regime=None, unified_confidence=50,
                timestamp_last_intel=0.0, sentinel_first_hit_at=0.0,
                timestamp_last_update=0.0, opened_at=0.0
            ))
            
            # 2. Clear Trade History
            print("Cleaning trade history (Vault)...")
            await session.execute(delete(TradeHistory))
            
            # 3. Reset Bankroll
            print("Resetting bankroll to $100.00...")
            res = await session.execute(select(BancaStatus).filter_by(id=1))
            banca = res.scalars().first()
            if banca:
                banca.saldo_total = 100.0
                banca.risco_real_percent = 0.0
                banca.slots_disponiveis = 4
                banca.status = "IDLE"
            else:
                session.add(BancaStatus(id=1, saldo_total=100.0, risco_real_percent=0.0, slots_disponiveis=4, status="IDLE"))

            # 4. Clear Moonbags
            print("Cleaning moonbags...")
            await session.execute(delete(Moonbag))

            # 5. Reset Vault Cycle
            print("Resetting vault cycles...")
            await session.execute(update(VaultCycle).values(
                sniper_wins=0, cycle_number=1, cycle_profit=0.0, cycle_losses=0.0,
                total_trades_cycle=0, cycle_gains_count=0, cycle_losses_count=0,
                vault_total=0.0, accumulated_vault=0.0
            ))

            # 6. Clear Paper Engine State
            print("Cleaning paper engine state...")
            await session.execute(delete(SystemState).where(SystemState.key == 'paper_engine_state'))

            await session.commit()
            print("[RESET-SOVEREIGN] System successfully reset to factory defaults.")
        except Exception as e:
            await session.rollback()
            print(f"Error during reset: {e}")

if __name__ == "__main__":
    asyncio.run(reset_system())
