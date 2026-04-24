# -*- coding: utf-8 -*-
import asyncio
import os
import sys
import logging
from datetime import datetime, timezone

# Ajustar path para importar serviços
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.firebase_service import firebase_service
from services.vault_service import VaultService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GoRealReset")

async def deep_clean():
    logger.info("🚀 INICIANDO LIMPEZA PROFUNDA (GO REAL PROTOCOL)...")
    
    await firebase_service.initialize()
    if not firebase_service.is_active:
        logger.error("❌ Falha ao conectar ao Firebase. Abortando.")
        return

    db = firebase_service.db
    rtdb = firebase_service.rtdb

    # 1. Limpar Coleções do Firestore
    collections_to_wipe = ["trade_history", "banca_history", "journey_signals", "system_logs"]
    
    async def delete_collection(coll_ref, batch_size=500):
        docs = coll_ref.limit(batch_size).stream()
        deleted = 0
        while True:
            batch = db.batch()
            batch_count = 0
            for doc in docs:
                batch.delete(doc.reference)
                batch_count += 1
            
            if batch_count == 0:
                break
            
            batch.commit()
            deleted += batch_count
            logger.info(f"   - Deletados {deleted} documentos...")
            docs = coll_ref.limit(batch_size).stream()
        return deleted

    for coll_name in collections_to_wipe:
        logger.info(f"🧹 Limpando coleção Firestore: {coll_name}...")
        count = await delete_collection(db.collection(coll_name))
        logger.info(f"✅ total de {count} documentos removidos de {coll_name}.")

    # 2. Resetar Slots Ativos
    logger.info("🎰 Resetando Slots Ativos no Firestore...")
    for i in range(1, 5):
        await firebase_service.update_slot(i, {
            "symbol": None,
            "entry_price": 0,
            "current_stop": 0,
            "entry_margin": 0,
            "status_risco": "LIVRE",
            "side": None,
            "pnl_percent": 0,
            "qty": 0,
            "opened_at": 0,
            "liq_price": 0,
            "target_price": 0,
            "timestamp_last_update": 0
        })
    logger.info("✅ 4 Slots resetados com sucesso.")

    # 3. Resetar Vault Cycle
    logger.info("🔒 Resetando Ciclo da Vault (Batalhão Pesado)...")
    vault = VaultService()
    default_cycle = vault._default_cycle()
    db.collection("vault_management").document("current_cycle").set(default_cycle)
    logger.info("✅ Ciclo da Vault reiniciado para o Padrão V35.0.")

    # 4. Resetar Banca Status
    logger.info("💰 Resetando Status da Banca...")
    db.collection("banca_status").document("status").set({
        "saldo_total": 0, # Será preenchido no primeiro boot REAL
        "configured_balance": 0,
        "risco_real_percent": 0,
        "slots_disponiveis": 4,
        "status": "RESET_FOR_REAL",
        "last_update": datetime.now(timezone.utc).isoformat()
    })
    logger.info("✅ Status da banca preparado.")

    # 5. Limpar Realtime Database (RTDB)
    if rtdb:
        logger.info("⚡ Limpando Realtime Database (RTDB)...")
        nodes_to_wipe = ["banca_status", "live_slots", "radar_pulse", "vault_status", "system_state"]
        for node in nodes_to_wipe:
            rtdb.child(node).delete()
        logger.info("✅ RTDB limpo com sucesso.")

    logger.info("✨ PROTOCOLO GO-REAL CONCLUÍDO COM SUCESSO! ✨")
    logger.info("Próximos passos:")
    logger.info("1. Alterar BYBIT_EXECUTION_MODE=REAL no .env")
    logger.info("2. Reiniciar o backend.")

if __name__ == "__main__":
    asyncio.run(deep_clean())
