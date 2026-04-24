# -*- coding: utf-8 -*-
import asyncio
from services.firebase_service import firebase_service
from services.bybit_rest import bybit_rest_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RectifyBanca")

async def rectify():
    await firebase_service.initialize()
    if not firebase_service.is_active:
        logger.error("Firebase not active. Check credentials.")
        return

    logger.info("Starting Paper Banca Rectification...")
    
    # 1. Reset Banca Status
    new_status = {
        "configured_balance": 100.0,
        "saldo_total": 100.0,
        "lucro_total_acumulado": 0.0,
        "risco_real_percent": 0.0,
        "slots_disponiveis": 4,
        "id": "status"
    }
    await firebase_service.update_banca_status(new_status)
    logger.info("✅ Banca status reset to $100.00")

    # 2. Hard Reset all Slots (1-4)
    for i in range(1, 5):
        await firebase_service.hard_reset_slot(i, reason="MANUAL_RECTIFICATION_V96.9")
    logger.info("✅ All 4 slots cleared.")

    # 3. Reset Paper State in Memory/Local File
    bybit_rest_service.paper_balance = 100.0
    bybit_rest_service.paper_positions = []
    bybit_rest_service._save_paper_state()
    logger.info("✅ Local paper state reset.")

    logger.info("🚀 RECTIFICATION COMPLETE. System ready for clean Paper Mode testing.")

if __name__ == "__main__":
    asyncio.run(rectify())
