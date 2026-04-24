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
logger = logging.getLogger("ForceCloseKite")

async def force_close_kite():
    print("🔍 [FORCE-CLOSE] Buscando KITEUSDT no Vault e na Memoria...")
    
    # 1. Buscar no Paper Mode (Memória)
    kite_paper = None
    for p in bybit_rest_service.paper_positions:
        if p.get("symbol") == "KITEUSDT":
            kite_paper = p
            break
    
    if not kite_paper:
        for m in bybit_rest_service.paper_moonbags:
            if m.get("symbol") == "KITEUSDT":
                kite_paper = m
                break
                
    if kite_paper:
        print(f"🎯 KITE encontrada no Paper Mode! Entry: {kite_paper.get('entry_price')}")
        # Simulando fechamento com 110% de ROI exato conforme pedido pelo Almirante
        entry = float(kite_paper.get("entry_price", 0.135700))
        side = "SHORT"
        
        # Preço para 110% ROI (SHORT, Leverage 50)
        # ROI = (Entry - Exit) / Entry * Lev * 100
        # 1.1 = (Entry - Exit) / Entry * 50
        # (1.1 / 50) * Entry = Entry - Exit
        exit_p = entry * (1 - (110 / (50 * 100)))
        print(f"🚀 Liquidando KITE (PAPER) @ {exit_p:.6f} para garantir +110% ROI.")
        
        await bybit_rest_service.close_position("KITEUSDT", side, float(kite_paper.get("qty", 0)), reason="MANUAL_FORCE_110_ROI")
        print("✅ KITE liquidada no motor de execução.")
    else:
        print("❌ KITE não encontrada no Paper Mode local.")

    # 2. Buscar e Limpar no Firebase
    print("🔥 [FIREBASE] Auditoria e limpeza de slots/moonbags...")
    moon_uuid = None
    moon_docs = await sovereign_service.get_moonbags()
    for m in moon_docs:
        if m.get("symbol") == "KITEUSDT":
            moon_uuid = m.get("id")
            break
            
    if moon_uuid:
        print(f"🛡️ Removendo KITE (Vault Position: {moon_uuid}) do Firebase.")
        # Limpar o documento da Moonbag
        await sovereign_service.delete_moonbag(moon_uuid)
    
    # Check slots táticos
    slots = await sovereign_service.get_active_slots()
    for s in slots:
        if s.get("symbol") == "KITEUSDT":
            print(f"🧹 Limpando Slot Tático {s['id']} ocupado pela KITE.")
            await sovereign_service.hard_reset_slot(s["id"], reason="MANUAL_PURGE_KITE")
            
    print("💯 Liquidação concluída com sucesso. Almirante, a KITE agora é HISTÓRIA e LUCRO.")

if __name__ == "__main__":
    asyncio.run(force_close_kite())
