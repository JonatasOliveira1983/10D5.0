import asyncio
import os
import sys
import logging

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sovereign_service import sovereign_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CleanSignals")

async def clean_collection(col_name, limit=100):
    logger.info(f"🧹 Clearing {col_name} (limit {limit} per batch)...")
    await sovereign_service.initialize()
    if not sovereign_service.is_active:
        logger.error("❌ Firebase not active.")
        return

    while True:
        docs = list(sovereign_service.db.collection(col_name).limit(limit).stream())
        if not docs:
            break
            
        batch = sovereign_service.db.batch()
        for doc in docs:
            batch.delete(doc.reference)
        
        await asyncio.to_thread(batch.commit)
        logger.info(f"✅ Deleted {len(docs)} docs from {col_name}...")
        await asyncio.sleep(0.5)

async def main():
    await clean_collection("journey_signals")
    await clean_collection("system_logs")

if __name__ == "__main__":
    asyncio.run(main())
