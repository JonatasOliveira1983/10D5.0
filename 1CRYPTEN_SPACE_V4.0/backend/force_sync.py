import asyncio
import logging
from dotenv import load_dotenv
load_dotenv()
from services.bankroll import bankroll_manager

logging.basicConfig(level=logging.INFO)

async def run_sync():
    print("Forcing bankroll update...")
    await bankroll_manager.update_banca_status()
    print("Done. Checking Firebase:")
    from services.sovereign_service import sovereign_service
    status = await sovereign_service.get_banca_status()
    print("New Status:", status)

if __name__ == "__main__":
    asyncio.run(run_sync())
