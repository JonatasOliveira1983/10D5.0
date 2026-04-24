"""
Emergency RTDB Cleaner - Forces banca_status in Realtime Database to $100 paper mode.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sovereign_service import sovereign_service

async def fix():
    print("🔧 Initializing Firebase...")
    await sovereign_service.initialize()
    
    if not sovereign_service.rtdb:
        print("❌ RTDB not connected!")
        return
    
    print("🔧 Forcing RTDB banca_status to $100 PAPER mode...")
    
    # Use .set() to REPLACE the entire node (not merge)
    clean_banca = {
        "configured_balance": 100.0,
        "saldo_total": 100.0,
        "saldo_real_bybit": 0.0,
        "risco_real_percent": 0.0,
        "slots_disponiveis": 4,
        "lucro_total_acumulado": 0.0,
        "lucro_ciclo": 0.0,
        "vault_total": 0.0,
        "leverage": 50
    }
    
    sovereign_service.rtdb.child("banca_status").set(clean_banca)
    print("✅ RTDB banca_status REPLACED with $100.00")
    
    # Also clean vault_status in RTDB
    clean_vault = {
        "cycle_number": 1,
        "mega_cycle_wins": 0,
        "cycle_profit": 0.0,
        "vault_total": 0.0,
        "cycle_start_bankroll": 100.0,
        "used_symbols_in_cycle": [],
        "next_entry_value": 10.0
    }
    sovereign_service.rtdb.child("vault_status").set(clean_vault)
    print("✅ RTDB vault_status REPLACED with clean cycle")
    
    print("🎯 RTDB Fix Complete!")

if __name__ == "__main__":
    asyncio.run(fix())
