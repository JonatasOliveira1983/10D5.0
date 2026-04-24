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
logger = logging.getLogger("RescueIPUSDT-Final")

async def rescue():
    await sovereign_service.initialize()
    print("🚑 [RESCUE-IPUSDT] Iniciando operação de resgate final...")

    symbol = "IPUSDT"
    entry = 0.5064
    leverage = 50
    margin = 9.36
    # 110% ROI Stop: Entry * (1 + 110/5000) = 0.517541
    target_stop = 0.517541
    opened_at = 1712383560 # 06/04 03:06
    
    moon_id = f"{symbol}_RESCUE_V110"

    # 1. Dados da Moonbag
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

    # 2. Gravação Síncrona via to_thread (ID FIXO)
    def force_write():
        doc_ref = sovereign_service.db.collection("moonbags").document(moon_id)
        doc_ref.set(moon_data)
        if sovereign_service.rtdb:
            sovereign_service.rtdb.child("moonbag_vault").child(moon_id).set(moon_data)
        # Limpar Slot 1
        sovereign_service.db.collection("slots").document("1").update({
            "symbol": None, "pnl_percent": 0, "status_risco": "LIVRE", "side": None
        })
        if sovereign_service.rtdb:
            sovereign_service.rtdb.child("slots").child("1").update({
                "symbol": None, "pnl_percent": 0, "status_risco": "LIVRE"
            })

    print(f"📝 Executando escrita atômica no Firestore/RTDB...")
    await asyncio.to_thread(force_write)
    
    # 3. Injetar na RAM do Motor
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
    
    bybit_rest_service.paper_positions = [p for p in bybit_rest_service.paper_positions if p.get("symbol") != symbol]
    bybit_rest_service.paper_moonbags = [m for m in bybit_rest_service.paper_moonbags if m.get("symbol") != symbol]
    bybit_rest_service.paper_moonbags.append(pos_obj)
    bybit_rest_service._save_paper_state()
    
    print(f"✅ [SUCESSO] IPUSDT resgatada. Saldo e Moonbags sincronizados.")
    print(f"🛡️ Profit-Lock: +110% ROI em ${target_stop:.6f}")

if __name__ == "__main__":
    asyncio.run(rescue())
