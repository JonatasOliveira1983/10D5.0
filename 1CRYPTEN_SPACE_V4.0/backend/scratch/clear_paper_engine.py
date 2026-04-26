import asyncio
import logging
import json
import sys
import os

# Adiciona o diretório atual ao path para encontrar 'services'
sys.path.append(os.getcwd())

from services.database_service import database_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClearPaperEngine")

async def clear_engine():
    logger.info("🧹 Starting Paper Engine State wipe...")
    
    # 1. Limpar paper_engine_state
    try:
        await database_service.save_system_state("paper_engine_state", {})
        logger.info("✅ paper_engine_state cleared in DB.")
    except Exception as e:
        logger.error(f"❌ Failed to clear paper_engine_state: {e}")

    # 2. Limpar paper_moonbag_state
    try:
        await database_service.save_system_state("paper_moonbag_state", [])
        logger.info("✅ paper_moonbag_state cleared in DB.")
    except Exception as e:
        logger.error(f"❌ Failed to clear paper_moonbag_state: {e}")

    # 3. Limpar Slots (Opcional, mas garante)
    try:
        for i in range(1, 5):
            await database_service.update_slot(i, {
                "symbol": None,
                "status_risco": "LIVRE",
                "pnl_percent": 0,
                "entry_price": 0,
                "order_id": None,
                "genesis_id": None
            })
        logger.info("✅ All slots cleared in DB.")
    except Exception as e:
        logger.error(f"❌ Failed to clear slots: {e}")

    logger.info("🚀 Wipe complete. Restart the bot for full effect.")

if __name__ == "__main__":
    asyncio.run(clear_engine())
