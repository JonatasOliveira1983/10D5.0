# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import json
from services.firebase_service import firebase_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RestoreStructural")

async def restore_and_sync():
    logger.info("🚀 Restoring Structural Stops and Sincronizing State...")
    
    # 1. Initialize Firebase
    await firebase_service.initialize()
    await firebase_service.initialize_db()
    
    # 2. Restore exact values requested/observed for the 4 slots
    # These match the structural breathing room (~1.4% - 2.0%)
    updates = {
        1: {"current_stop": 54.13},       # LTCUSDT
        2: {"current_stop": 623.74},      # BNBUSDT
        3: {"current_stop": 453.59},      # BCHUSDT
        4: {"current_stop": 8.68385714}   # LINKUSDT ($8.68)
    }
    
    for slot_id, data in updates.items():
        logger.info(f"📏 Restoring Slot {slot_id} SL to structural: {data['current_stop']}")
        await firebase_service.update_slot(slot_id, data)

    # 3. Nuke local Paper Storage to force re-adoption
    paper_file = "paper_storage.json"
    if os.path.exists(paper_file):
        try:
            logger.info(f"💥 Nuking local {paper_file} to clear memory ghosts...")
            with open(paper_file, 'w') as f:
                json.dump({"positions": [], "balance": 100.0, "history": []}, f, indent=2)
            logger.info("✅ Paper Storage reset.")
        except Exception as e:
            logger.error(f"❌ Failed to nuke paper storage: {e}")

    logger.info("🏁 Restoration and Sync Complete.")

if __name__ == "__main__":
    asyncio.run(restore_and_sync())
