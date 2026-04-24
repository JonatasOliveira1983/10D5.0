# -*- coding: utf-8 -*-
import asyncio
import sys
import os
import logging

# Adicionar path do backend
sys.path.append(os.getcwd())

from services.bankroll import bankroll_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ForceSyncV110")

async def force_sync():
    print("🔄 [FORCE-SYNC] Sincronizando slots com o motor de execução...")
    await bankroll_manager.sync_slots_with_exchange()
    print("✅ Sincronização concluída. Verifique o dashboard agora.")

if __name__ == "__main__":
    asyncio.run(force_sync())
