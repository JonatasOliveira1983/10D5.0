import asyncio
from services.sovereign_service import sovereign_service
import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

async def clear_slot_2():
    await sovereign_service.initialize()
    print("[PURGE] Forcando liberacao do Slot 2 (BTCUSDT)...")
    await sovereign_service.free_slot(2, reason="REMOVIDO: Blue Chip Blocklist V110.168")
    print("Slot 2 limpo no banco de dados. Para limpar o paper_storage.json, farei manualmente ou com python.")

if __name__ == "__main__":
    asyncio.run(clear_slot_2())
