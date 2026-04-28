# fresh_start.py - 1CRYPTEN_SPACE_V4.0 Master Reset (Estado Zero)
import asyncio
import os
import sys
import json
from datetime import datetime, timezone

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from services.database_service import database_service, TradeHistory, OrderGenesis, VaultCycle, VaultWithdrawal, Slot, BancaStatus, SystemState
from sqlalchemy import delete

async def fresh_start():
    print("☢️  [MASTER-RESET] Iniciando Protocolo ESTADO ZERO (Fresh Start)...")
    
    # 1. Initialize Database
    await database_service.initialize()
    
    async with database_service.AsyncSessionLocal() as session:
        try:
            # 2. Limpar Slots
            print("🧹 Limpando todos os slots no Postgres...")
            for i in range(1, 5):
                slot_data = {
                    "symbol": None,
                    "status_risco": "LIVRE",
                    "pnl_percent": 0.0,
                    "pnl_usd": 0.0,
                    "entry_price": 0.0,
                    "current_stop": 0.0,
                    "target_price": 0.0,
                    "qty": 0.0,
                    "side": None,
                    "order_id": None,
                    "genesis_id": None,
                    "timestamp_last_update": 0.0,
                    "pensamento": "🔄 Reset Manual: Estado Zero"
                }
                await database_service.update_slot(i, slot_data)
            print("   ✅ Slots resetados.")

            # 3. Purgar Histórico de Trades
            print("\n🗑️  Purgando Histórico de Trades...")
            await session.execute(delete(TradeHistory))
            print("   ✅ Tabela trade_history limpa.")

            # 4. Purgar Gênese de Ordens
            print("\n🗑️  Purgando Gênese de Ordens...")
            await session.execute(delete(OrderGenesis))
            print("   ✅ Tabela order_genesis limpa.")

            # 5. Purgar Retiradas da Vault
            print("\n🗑️  Purgando Retiradas da Vault...")
            await session.execute(delete(VaultWithdrawal))
            print("   ✅ Tabela vault_withdrawals limpa.")

            # 6. Resetar Ciclo da Vault
            print("\n🔄 Resetando Ciclo da Vault para o Estado Inicial (Ciclo #1)...")
            await session.execute(delete(VaultCycle))
            await session.commit() # Commit deletes first
            
            default_vault = {
                "id": 1,
                "sniper_wins": 0,
                "cycle_number": 1,
                "cycle_profit": 0.0,
                "cycle_losses": 0.0,
                "started_at": datetime.now(timezone.utc).replace(tzinfo=None),
                "in_admiral_rest": False,
                "vault_total": 0.0,
                "cautious_mode": False,
                "min_score_threshold": 75,
                "total_trades_cycle": 0,
                "cycle_gains_count": 0,
                "cycle_losses_count": 0,
                "accumulated_vault": 0.0,
                "used_symbols_in_cycle": [],
                "cycle_start_bankroll": 100.0,
                "next_entry_value": 10.0,
                "mega_cycle_wins": 0,
                "mega_cycle_total": 0,
                "mega_cycle_number": 1,
                "mega_cycle_profit": 0.0,
                "order_ids_processed": []
            }
            new_vault = VaultCycle(**default_vault)
            session.add(new_vault)
            print("   ✅ Vault resetada para Ciclo #1.")

            # 7. Resetar Banca para $100
            print("\n💰 Resetando Banca para $100.00...")
            banca_data = {
                "saldo_total": 100.0,
                "risco_real_percent": 0.0,
                "slots_disponiveis": 4,
                "status": "IDLE"
            }
            await database_service.update_banca_status(banca_data)
            
            # 8. Limpar Estado do Motor Paper
            print("\n📄 Limpando Estado do Motor Paper (system_state)...")
            await session.execute(delete(SystemState).where(SystemState.key == "paper_engine_state"))
            
            # Limpar arquivo físico se existir
            paper_path = os.path.join(backend_dir, "paper_storage.json")
            if os.path.exists(paper_path):
                empty_paper = {"positions": [], "updated_at": 0}
                with open(paper_path, 'w') as f:
                    json.dump(empty_paper, f, indent=2)
                print("   ✅ paper_storage.json limpo.")

            await session.commit()
            print("\n✨ [FRESH START COMPLETO] O sistema está em Estado Zero.")
            print("🚀 Pronto para iniciar um novo ciclo de Elite.")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ ERRO DURANTE O RESET: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fresh_start())
