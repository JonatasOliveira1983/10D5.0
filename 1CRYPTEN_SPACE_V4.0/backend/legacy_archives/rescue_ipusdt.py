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
from services.bankroll import bankroll_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RescueIPUSDT-Final")

async def rescue():
    await sovereign_service.initialize()
    print("🚑 [RESCUE-IPUSDT-FINAL] Iniciando operação de resgate...")

    # 1. Dados da Ordem (Baseado no log do Almirante)
    symbol = "IPUSDT"
    entry_price = 0.5064
    side = "Buy"
    leverage = 50
    margin = 9.36
    # 06/04 03:06 -> Timestamp aproximado
    opened_at = 1712383560 
    slot_id = 1

    # 2. Injetar na RAM do BybitREST (Coração do motor)
    pos_obj = {
        "symbol": symbol,
        "side": side,
        "size": str(margin * leverage / entry_price),
        "avgPrice": str(entry_price),
        "leverage": str(leverage),
        "status": "TRADING",
        "createdTime": str(int(opened_at * 1000)),
        "opened_at": opened_at,
        "updatedTime": str(int(time.time() * 1000)),
        "stopLoss": "0.4967",
        "takeProfit": "0",
        "slot_id": slot_id,
        "entry_margin": margin
    }

    bybit_rest_service.paper_positions = [p for p in bybit_rest_service.paper_positions if p.get("symbol") != symbol]
    bybit_rest_service.paper_positions.append(pos_obj)
    await bybit_rest_service._save_paper_state()
    print("🧠 [RAM/DISCO] IPUSDT re-adotada com sucesso.")

    # 3. Forçar Promoção no Firebase
    # Sincroniza o slot primeiro para garantir que o opened_at esteja lá
    await sovereign_service.update_slot(slot_id, {
        "symbol": f"{symbol}.P",
        "side": side,
        "entry_price": entry_price,
        "opened_at": opened_at,
        "status_risco": "EMANCIPATION_READY",
        "slot_type": "SWING"
    })
    
    # Promove
    moon_uuid = await sovereign_service.promote_to_moonbag(slot_id)
    if moon_uuid:
        # 110% ROI Stop
        new_stop = entry_price * (1 + (110.0 / (leverage * 100)))
        new_stop = await bybit_rest_service.round_price(symbol, new_stop)
        
        # Update Final com SET (merge=True) para evitar 404
        update_data = {
            "current_stop": new_stop,
            "is_emancipated": True,
            "status": "EMANCIPATED",
            "pnl_percent": 132.6,
            "timestamp_last_update": time.time()
        }
        await asyncio.to_thread(sovereign_service.db.collection("moonbags").document(moon_uuid).set, update_data, merge=True)
        
        # Mover na memória de moonbags
        pos_obj["status"] = "EMANCIPATED"
        pos_obj["stopLoss"] = str(new_stop)
        if pos_obj in bybit_rest_service.paper_positions:
            bybit_rest_service.paper_positions.remove(pos_obj)
        bybit_rest_service.paper_moonbags.append(pos_obj)
        await bybit_rest_service._save_paper_state()
        
        print(f"✅ [SUCESSO] IPUSDT emancipada no Vault com ID: {moon_uuid}")
        print(f"🛡️ Profit-Lock: +110% ROI em ${new_stop:.6f}")
    else:
        print("❌ Erro ao promover via API.")

if __name__ == "__main__":
    asyncio.run(rescue())
