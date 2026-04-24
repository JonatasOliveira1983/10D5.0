# -*- coding: utf-8 -*-
import asyncio
import sys
import os
import time
import logging
import uuid
from datetime import datetime

# Adicionar path do backend
sys.path.append(os.getcwd())

from services.sovereign_service import sovereign_service
from services.bybit_rest import bybit_rest_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RescueIPUSDT-Ultra")

async def ultra_rescue():
    await sovereign_service.initialize()
    print("🚀 [ULTRA-RESCUE] IPUSDT - Iniciando...")

    symbol = "IPUSDT"
    entry = 0.5064
    leverage = 50
    margin = 9.36
    # 110% ROI Stop: Entry * (1 + 110/5000) = 0.517541
    target_stop = 0.517541
    opened_at = 1712383560 # 06/04 03:06
    
    # ID determinístico para a Moonbag
    moon_id = f"{symbol}_RESCUE_{int(time.time())}"

    # 1. Injetar diretamente no Firestore (Moonbags)
    moon_data = {
        "id": moon_id,
        "symbol": symbol,
        "side": "Buy",
        "entry_price": entry,
        "qty": (margin * leverage) / entry,
        "leverage": leverage,
        "current_stop": target_stop,
        "opened_at": opened_at,
        "emancipated_at": time.time(),
        "is_emancipated": True,
        "status": "EMANCIPATED",
        "pnl_percent": 132.6,
        "slot_type": "SWING",
        "visual_status": "SURFING",
        "strategy": "ETERNAL_SURF"
    }

    print(f"📝 Gravando Moonbag no Firestore: {moon_id}")
    await asyncio.to_thread(sovereign_service.db.collection("moonbags").document(moon_id).set, moon_data)
    
    # 2. Atualizar RTDB (Vault)
    if sovereign_service.rtdb:
        print("⚡ Gravando no RTDB Vault...")
        await asyncio.to_thread(sovereign_service.rtdb.child("moonbag_vault").child(moon_id).set, moon_data)

    # 3. Limpar o Slot 1 (Liberação)
    print("🧹 Liberando Slot 1...")
    await sovereign_service.hard_reset_slot(1, "RESCUE_CLEANUP", pnl=0.0)

    # 4. Injetar na RAM do Motor (BybitREST)
    # Importante para o motor monitorar o SL de 110%
    pos_obj = {
        "symbol": symbol,
        "side": "Buy",
        "size": str(moon_data["qty"]),
        "avgPrice": str(entry),
        "leverage": str(leverage),
        "status": "EMANCIPATED",
        "stopLoss": str(target_stop),
        "takeProfit": "0",
        "is_paper": True,
        "entry_margin": margin,
        "opened_at": opened_at
    }
    
    # Remove duplicatas e adiciona em moonbags
    bybit_rest_service.paper_positions = [p for p in bybit_rest_service.paper_positions if p.get("symbol") != symbol]
    bybit_rest_service.paper_moonbags = [m for m in bybit_rest_service.paper_moonbags if m.get("symbol") != symbol]
    bybit_rest_service.paper_moonbags.append(pos_obj)
    await bybit_rest_service._save_paper_state()
    
    print(f"✅ [MISSÃO CUMPRIDA] IPUSDT agora é uma Moonbag Surfista!")
    print(f"🛡️ Stop Lock travado em 110% ROI: ${target_stop:.6f}")

if __name__ == "__main__":
    asyncio.run(ultra_rescue())
