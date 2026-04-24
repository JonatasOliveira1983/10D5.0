import argparse
import os
import sys
import asyncio
import logging
from config import settings

# Setup logging for CLI
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("1CRYPTEN-CLI")

def run_server():
    """Inicia o servidor FastAPI usando uvicorn."""
    import uvicorn
    logger.info(f"🚀 Iniciando servidor em {settings.HOST}:{settings.PORT}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=False)

async def sync_vault():
    """Sincroniza o Vault com o histórico do Firebase."""
    logger.info("🔄 Sincronizando Vault...")
    from services.vault_service import vault_service
    await vault_service.sync_vault_with_history()
    logger.info("✅ Sincronização concluída.")

async def nuke_paper():
    """Executa a limpeza total do estado Paper (Nuke)."""
    logger.warning("💥 EXECUTANDO NUKE TOTAL DO ESTADO...")
    from services.bybit_rest import bybit_rest_service
    from services.firebase_service import firebase_service
    
    # Inicializa Firebase SDK antes de usar
    await firebase_service.initialize()
    
    # 1. RAM Cleanup
    bybit_rest_service.paper_positions.clear()
    bybit_rest_service.paper_moonbags.clear()
    bybit_rest_service.paper_balance = 100.0
    bybit_rest_service._save_paper_state()
    
    # 2. Firebase Core Cleanup (Slots)
    for i in range(1, 5):
        await firebase_service.hard_reset_slot(i, "COMMANDER_NUKE", pnl=0.0)
    
    # 3. Firestore Collection Wipe (History & Logs)
    collections_to_wipe = ["trade_history", "journey_signals", "banca_history", "system_logs", "moonbags"]
    for col_name in collections_to_wipe:
        try:
            logger.info(f"🧹 Limpando coleção: {col_name}...")
            # Pega todos os documentos da coleção e deleta progressivamente
            docs = await asyncio.to_thread(firebase_service.db.collection(col_name).get)
            for doc in docs:
                await asyncio.to_thread(doc.reference.delete)
            logger.info(f"✅ Coleção {col_name} purgada.")
        except Exception as e:
            logger.error(f"❌ Erro ao limpar {col_name}: {e}")

    # 4. RTDB Cleanup
    if firebase_service.rtdb:
        try:
            logger.info("🧹 Limpando Realtime DB (Moonbags & Cooldowns)...")
            await asyncio.to_thread(firebase_service.rtdb.child("moonbag_vault").delete)
            await asyncio.to_thread(firebase_service.rtdb.child("system_cooldowns").delete)
            await asyncio.to_thread(firebase_service.rtdb.child("chat_history").delete)
        except Exception as e:
            logger.error(f"❌ Erro ao limpar RTDB: {e}")

    # 5. Reset Banca Status
    await firebase_service.update_banca_status({
        "saldo_total": 100.0,
        "risco_real_percent": 0.0,
        "slots_disponiveis": 4,
        "pnl_diario": 0.0,
        "pnl_mensal": 0.0,
        "status": "READY"
    })
    
    logger.info("🚀 [NUKE COMPLETE] Sistema restaurado para $100.00. Casco 100% íntegro.")

def main():
    parser = argparse.ArgumentParser(description="1CRYPTEN Management CLI")
    parser.add_argument("command", choices=["run", "sync", "nuke"], help="Comando a ser executado")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_server()
    elif args.command == "sync":
        asyncio.run(sync_vault())
    elif args.command == "nuke":
        asyncio.run(nuke_paper())

if __name__ == "__main__":
    main()
