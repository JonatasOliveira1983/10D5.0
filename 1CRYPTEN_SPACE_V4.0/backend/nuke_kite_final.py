# -*- coding: utf-8 -*-
import asyncio
import sys
import os
import time
import json
import logging

# Adicionar path do backend
sys.path.append(os.getcwd())

from services.firebase_service import firebase_service
from services.bybit_rest import bybit_rest_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NuclearWipeKite")

async def nuclear_wipe_kite():
    print("☢️ [NUCLEAR-WIPE] Iniciando erradicação total da KITEUSDT...")
    
    # 1. Limpeza de DISCO (Paper Storage)
    storage_file = "paper_positions.json"
    if os.path.exists(storage_file):
        try:
            with open(storage_file, 'r') as f:
                data = json.load(f)
            # Remove KITE de posições e moonbags do JSON
            if "positions" in data:
                data["positions"] = [p for p in data["positions"] if p.get("symbol") != "KITEUSDT"]
            if "moonbags" in data:
                data["moonbags"] = [m for m in data["moonbags"] if m.get("symbol") != "KITEUSDT"]
            
            with open(storage_file, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"📁 [DISCO] KITE removida do {storage_file}")
        except Exception as e:
            print(f"⚠️ Erro ao limpar disco: {e}")

    # 2. Limpeza de RAM
    bybit_rest_service.paper_positions = [p for p in bybit_rest_service.paper_positions if p.get("symbol") != "KITEUSDT"]
    bybit_rest_service.paper_moonbags = [m for m in bybit_rest_service.paper_moonbags if m.get("symbol") != "KITEUSDT"]
    if hasattr(bybit_rest_service, 'pending_closures'):
        bybit_rest_service.pending_closures = set([c for c in bybit_rest_service.pending_closures if c != "KITEUSDT"])
    print("🧠 [RAM] KITE removida da memória do BybitREST")

    # 3. Limpeza FIRESTORE (Atomic Delete)
    await firebase_service.initialize()
    m_fs = await firebase_service.get_moonbags()
    for m in m_fs:
        if m.get("symbol") == "KITEUSDT":
            print(f"🔥 [FIRESTORE] Deletando Moonbag: {m['id']}")
            # Use remove_moonbag para limpar RTDB e Firestore simultaneamente
            await firebase_service.remove_moonbag(m['id'], reason="NUCLEAR_WIPE_FORCE")
            
    # 4. Limpeza RTDB (Recursiva no rastro)
    if firebase_service.rtdb:
        print("⚡ [RTDB] Nuke nos nós moonbag_vault e slots...")
        vault = await asyncio.to_thread(firebase_service.rtdb.child("moonbag_vault").get)
        if vault:
            for k, v in vault.items():
                if v and v.get("symbol") == "KITEUSDT":
                    print(f"🗑️ Removendo KITE do RTDB moonbag_vault: {k}")
                    await asyncio.to_thread(firebase_service.rtdb.child("moonbag_vault").child(k).delete)
                    
        slots = await asyncio.to_thread(firebase_service.rtdb.child("slots").get)
        if slots:
            for sid, data in slots.items():
                if data and data.get("symbol") == "KITEUSDT":
                    print(f"🧹 Resetando KITE no RTDB slot: {sid}")
                    await asyncio.to_thread(firebase_service.rtdb.child("slots").child(sid).update, {
                        "symbol": None, "pnl_percent": 0, "status_risco": "LIVRE"
                    })

    print("💯 [NUCLEAR-WIPE] Erradicação concluída. Almirante, se ela voltar agora, ela é imortal.")

if __name__ == "__main__":
    asyncio.run(nuclear_wipe_kite())
