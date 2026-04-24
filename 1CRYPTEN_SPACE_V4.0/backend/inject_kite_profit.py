# -*- coding: utf-8 -*-
import asyncio
import sys
import os
import time
import logging
from datetime import datetime, timezone

# Adicionar path do backend
sys.path.append(os.getcwd())

from services.firebase_service import firebase_service
from services.bankroll import bankroll_manager
from services.time_utils import get_br_iso_str

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KiteProfitInjection")

async def inject_profit():
    print("💰 [KITE-INJECTION] Iniciando auditoria de lucro para KITEUSDT (+110% ROI)...")
    
    # 1. Definir parâmetros da KITE (Baseado nos logs do Almirante)
    symbol = "KITEUSDT"
    side = "Sell" # SHORT
    entry_price = 0.135700
    leverage = 50
    # Cálculo para 110% ROI
    # Exit = Entry * (1 - (ROI / (Lev * 100)))
    exit_price = entry_price * (1 - (110 / (leverage * 100))) 
    
    # Margem padrão de 10% da banca inicial de $100
    margin = 10.00
    pnl = 11.00 # 110% de $10.00
    
    # 2. Criar Trade Data para o Histórico (Vault History)
    report = f"--- AUDIT REPORT KITE REDEMPTION ---\n"
    report += f"SYMBOL: {symbol} | SIDE: {side}\n"
    report += f"ROI: +110.0% | PNL: ${pnl:.2f}\n"
    report += f"ENTRY: ${entry_price:.6f} | EXIT: ${exit_price:.6f}\n"
    report += f"REASON: MANUAL_PROFIT_LOCK_ALMIRANTE\n"
    report += f"-------------------------------------"
    
    trade_data = {
        "symbol": symbol,
        "side": side,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "qty": (margin * leverage) / entry_price, # Quantidade aproximada
        "pnl": pnl,
        "final_roi": 110.0,
        "slot_type": "MOONBAG",
        "close_reason": "MANUAL_PROFIT_LOCK",
        "closed_at": get_br_iso_str(),
        "reasoning_report": report,
        "timestamp": get_br_iso_str()
    }
    
    # 3. Registrar no Histórico do Firestore
    print(f"📝 Injetando trade no histórico (Vault)...")
    await firebase_service.log_trade(trade_data)
    
    # 4. Atualizar a Banca no Firestore e RTDB
    print(f"🏦 Atualizando saldo da banca (+$11.00)...")
    status = await firebase_service.get_banca_status()
    old_balance = status.get("saldo_total", 100.0)
    new_balance = old_balance + pnl
    
    new_status = {
        "saldo_total": new_balance,
        "lucro_acumulado": status.get("lucro_acumulado", 0) + pnl,
        "timestamp_last_update": time.time()
    }
    
    # Update Firestore
    await asyncio.to_thread(firebase_service.db.collection("banca_status").document("status").update, new_status)
    # Update RTDB
    if firebase_service.rtdb:
        await asyncio.to_thread(firebase_service.rtdb.child("banca_status/status").update, new_status)
        
    print(f"✅ [KITE-INJECTION] Lucro de $11.00 injetado com sucesso!")
    print(f"💰 Saldo Atualizado: ${new_balance:.2f} (Almirante, o lucro está em casa!)")

if __name__ == "__main__":
    asyncio.run(inject_profit())
