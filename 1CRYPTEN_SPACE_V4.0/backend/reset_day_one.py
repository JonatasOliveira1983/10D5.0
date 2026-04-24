# -*- coding: utf-8 -*-
import asyncio
import os
import json
import logging
import time
from services.sovereign_service import sovereign_service
from services.bybit_rest import bybit_rest_service
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResetDayOne")

async def run_reset():
    logger.info("🚀 Iniciando Reset Total: 10D-3.0 (MODO PAPER - DIA 1)")
    
    # 1. Initialize Firebase
    await sovereign_service.initialize()
    if not sovereign_service.is_active:
        logger.error("❌ Erro ao conectar ao Firebase. Abortando.")
        return

    # 2. Reset Banca Status (Configured $100)
    logger.info("💰 Resetando Banca para $100.00...")
    banca_reset = {
        "saldo_total": 100.0,
        "configured_balance": 100.0,
        "risco_real_percent": 0.0,
        "slots_disponiveis": 4,
        "status": "ONLINE",
        "timestamp_last_update": time.time()
    }
    await sovereign_service.update_banca_status(banca_reset)

    # 3. Limpar Slots Ativos (ID 1 a 4)
    logger.info("🧹 Limpando os 4 slots táticos...")
    for i in range(1, 5):
        logger.info(f"   Resetando Slot {i}...")
        await sovereign_service.hard_reset_slot(i, reason="RESET_DAY_ONE")

    # 4. Limpar Trade History (Firestore)
    logger.info("📜 Deletando histórico de trades...")
    trade_docs = await asyncio.to_thread(sovereign_service.db.collection("trade_history").get)
    deleted_hist = 0
    for doc in trade_docs:
        await asyncio.to_thread(doc.reference.delete)
        deleted_hist += 1
    logger.info(f"   {deleted_hist} registros de histórico deletados.")

    # 5. Limpar Moonbag Vault (Firestore & RTDB)
    logger.info("🌔 Esvaziando o Moonbag Vault...")
    moon_docs = await asyncio.to_thread(sovereign_service.db.collection("moonbags").get)
    deleted_moon = 0
    for doc in moon_docs:
        await asyncio.to_thread(doc.reference.delete)
        deleted_moon += 1
    
    # Esvaziar RTDB moonbag_vault (se ativo)
    if sovereign_service.rtdb:
         await asyncio.to_thread(sovereign_service.rtdb.child("moonbag_vault").set, {})
    
    logger.info(f"   {deleted_moon} moonbags removidas do Vault.")

    # 6. Limpar Journey Signals (Opcional, mas recomendado para o 'Dia 1')
    logger.info("📡 Limpando sinais de jornada anteriores...")
    signal_docs = await asyncio.to_thread(sovereign_service.db.collection("journey_signals").get)
    deleted_sig = 0
    for doc in signal_docs:
        await asyncio.to_thread(doc.reference.delete)
        deleted_sig += 1
    logger.info(f"   {deleted_sig} sinais de jornada limpos.")

    # 7. Limpar Paper Storage Local
    logger.info("📂 Limpando persistência local do modo Paper...")
    if os.path.exists(bybit_rest_service.PAPER_STORAGE_FILE):
        try:
            os.remove(bybit_rest_service.PAPER_STORAGE_FILE)
            logger.info(f"   Arquivo {bybit_rest_service.PAPER_STORAGE_FILE} deletado.")
        except Exception as e:
            logger.error(f"   Erro ao deletar arquivo local: {e}")
    else:
        logger.info("   Arquivo de storage local não encontrado.")

    logger.info("✅ RESET COMPLETO! O sistema está pronto para o 'Dia 1'.")

if __name__ == "__main__":
    asyncio.run(run_reset())
