# -*- coding: utf-8 -*-
import asyncio
import sys
import os
import time
import logging

# Adicionar path do backend
sys.path.append(os.getcwd())

from services.sovereign_service import sovereign_service
from services.bybit_rest import bybit_rest_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepWipeKite")

async def deep_wipe_kite():
    print("🧹 [DEEP-WIPE] Iniciando limpeza atômica da KITEUSDT...")
    
    # 1. Limpeza Firestore
    print("🔥 [Firestore] Verificando moonbags e slots...")
    moon_docs = await sovereign_service.get_moonbags()
    for m in moon_docs:
        if m.get("symbol") == "KITEUSDT":
            print(f"🗑️ Deletando Moonbag Firestore: {m['id']}")
            await sovereign_service.remove_moonbag(m['id'], reason="DEEP_WIPE_FORCE")
            
    slots = await sovereign_service.get_active_slots()
    for s in slots:
        if s.get("symbol") == "KITEUSDT":
            print(f"🧹 Limpando Slot Firestore: {s['id']}")
            await sovereign_service.hard_reset_slot(s['id'], reason="DEEP_WIPE_FORCE")

    # 2. Limpeza Realtime Database (RTDB) - MUITO IMPORTANTE PARA A UI
    if sovereign_service.rtdb:
        print("⚡ [RTDB] Verificando rastro da KITE no Realtime Database...")
        try:
            # Limpar Moonbags no RTDB
            moon_vault = await asyncio.to_thread(sovereign_service.rtdb.child("moonbag_vault").get)
            if moon_vault:
                for uuid, data in moon_vault.items():
                    if data and data.get("symbol") == "KITEUSDT":
                        print(f"🗑️ Removendo KITE do RTDB moonbag_vault: {uuid}")
                        await asyncio.to_thread(sovereign_service.rtdb.child("moonbag_vault").child(uuid).delete)
            
            # Limpar Slots no RTDB
            rtdb_slots = await asyncio.to_thread(sovereign_service.rtdb.child("slots").get)
            if rtdb_slots:
                for slot_id, data in rtdb_slots.items():
                    if data and data.get("symbol") == "KITEUSDT":
                        print(f"🧹 Resetando KITE no RTDB slots: {slot_id}")
                        # Reset para estado livre
                        await asyncio.to_thread(sovereign_service.rtdb.child("slots").child(slot_id).update, {
                            "symbol": None, "pnl_percent": 0, "status_risco": "LIVRE"
                        })
        except Exception as e:
            print(f"⚠️ Erro ao limpar RTDB: {e}")

    # 3. Limpeza Memória Paper Mode
    print("📝 [PaperMode] Verificando motor de execução...")
    bybit_rest_service.paper_positions = [p for p in bybit_rest_service.paper_positions if p.get("symbol") != "KITEUSDT"]
    bybit_rest_service.paper_moonbags = [m for m in bybit_rest_service.paper_moonbags if m.get("symbol") != "KITEUSDT"]
    if "KITEUSDT" in bybit_rest_service.pending_closures:
        bybit_rest_service.pending_closures.remove("KITEUSDT")
        
    print("✅ [DEEP-WIPE] KITEUSDT foi erradicada de todas as dimensões.")

if __name__ == "__main__":
    asyncio.run(deep_wipe_kite())
