# -*- coding: utf-8 -*-
import asyncio
import sys
import os
import logging

# Adicionar path do backend
sys.path.append(os.getcwd())

from services.sovereign_service import sovereign_service
from services.bybit_rest import bybit_rest_service
from services.execution_protocol import execution_protocol

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuditIPUSDT")

async def audit():
    await sovereign_service.initialize()
    
    print("🔍 [AUDIT-IPUSDT] Verificando estado atual...")
    
    # 1. Procurar nos Slots Ativos
    slots = await sovereign_service.get_active_slots()
    ip_slot = next((s for s in slots if s.get("symbol") == "IPUSDT.P" or s.get("symbol") == "IPUSDT"), None)
    
    if ip_slot:
        print(f"✅ Slot Encontrado: ID {ip_slot.get('id')}")
        print(f"   ROI Atual: {ip_slot.get('pnl_percent')}%")
        print(f"   Status Risco: {ip_slot.get('status_risco')}")
        print(f"   Emancipated: {ip_slot.get('is_emancipated')}")
        print(f"   Slot Type: {ip_slot.get('slot_type')}")
    else:
        print("❌ IPUSDT não encontrada nos slots ativos do Firestore.")

    # 2. Procurar na Memória do BybitREST (Paper)
    ip_paper = next((p for p in bybit_rest_service.paper_positions if p.get("symbol") == "IPUSDT"), None)
    if ip_paper:
        print(f"✅ Posição em RAM (BybitREST): Found")
        print(f"   Status: {ip_paper.get('status')}")
    else:
        print("❌ IPUSDT não encontrada na memória paper_positions.")
        
    # 3. Verificar travas de emancipação
    is_locked = "IPUSDT" in bybit_rest_service.emancipating_symbols
    print(f"🔒 Trava de Emancipação Ativa? {is_locked}")

    # 4. Simulação de Lógica
    if ip_slot:
        roi = float(ip_slot.get("pnl_percent", 0))
        slot_type = ip_slot.get("slot_type", "SNIPER")
        is_emancipated = ip_slot.get("is_emancipated", False)
        
        print(f"🧪 Testando Gatilho (ROI={roi}%):")
        trigger = roi >= 150.0 and not is_emancipated and slot_type in ["TREND", "SWING", "SNIPER", "SCALP"]
        print(f"   Gatilho Dispararia? {trigger}")

if __name__ == "__main__":
    asyncio.run(audit())
