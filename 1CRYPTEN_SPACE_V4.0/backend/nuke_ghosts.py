# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import json
from services.firebase_service import firebase_service
from services.bybit_rest import bybit_rest_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NukeGhosts")

async def nuke_ghosts_and_align_sl():
    logger.info("🚀 Starting Ghost Vaporization and SL Alignment...")
    
    # 1. Initialize Firebase
    await firebase_service.initialize()
    await firebase_service.initialize_db()
    
    # 2. Align Firestore SLs to 1% (Maximum)
    slots = await firebase_service.get_active_slots()
    for slot in slots:
        symbol = slot.get("symbol")
        if not symbol: continue
        
        entry = float(slot.get("entry_price", 0))
        current_sl = float(slot.get("current_stop", 0))
        side = slot.get("side", "Buy")
        
        if entry <= 0: continue
        
        # Calculate 1% stop price
        limit_sl = entry * 1.01 if side == "Sell" else entry * 0.99
        
        # Check if current SL is wider than 1%
        is_wider = False
        if side == "Buy" and current_sl < limit_sl:
            is_wider = True
        elif side == "Sell" and current_sl > limit_sl:
            is_wider = True
            
        if is_wider:
            logger.info(f"📏 Aligning SL for {symbol}: {current_sl} -> {limit_sl} (1% limit)")
            await firebase_service.update_slot(slot["id"], {"current_stop": limit_sl})
        else:
            logger.info(f"✅ SL for {symbol} is already within 1% limit ({current_sl})")

    # 3. Nuke local Paper Storage
    paper_file = "paper_storage.json"
    if os.path.exists(paper_file):
        try:
            logger.info(f"💥 Nuking local {paper_file}...")
            # We don't delete, we reset to clean state to avoid startup errors
            with open(paper_file, 'w') as f:
                json.dump({"positions": [], "balance": 100.0, "history": []}, f, indent=2)
            logger.info("✅ Paper Storage reset.")
        except Exception as e:
            logger.error(f"❌ Failed to nuke paper storage: {e}")
    else:
        logger.info("ℹ️ No local paper_storage.json found.")

    logger.info("🏁 Nuke and Alignment Complete.")

if __name__ == "__main__":
    asyncio.run(nuke_ghosts_and_align_sl())
