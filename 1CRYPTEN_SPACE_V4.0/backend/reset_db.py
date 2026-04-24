import asyncio
import sys
import os

# Ensure backend module can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.firebase_service import firebase_service
from services.vault_service import vault_service

async def reset():
    print("Starting Deep Reset...")
    await firebase_service.initialize()
    
    print("1. Clearing Slots 1 to 4...")
    empty_slot = {
        "symbol": None, "entry_price": 0, "current_stop": 0, "entry_margin": 0,
        "status_risco": "IDLE", "side": None, "pnl_percent": 0, "target_price": 0,
        "qty": 0, "slot_type": None, "pattern": None, "pensamento": ""
    }
    
    for i in range(1, 5):
        try:
            await firebase_service.update_slot(i, empty_slot)
            print(f"  Slot {i} reset to IDLE.")
        except Exception as e:
            print(f"  Error resetting slot {i}: {e}")

    print("2. Clearing Trade History...")
    try:
        db = firebase_service.db
        trades = db.collection("trade_history").limit(500).stream()
        count = 0
        for doc in trades:
            doc.reference.delete()
            count += 1
        print(f"  Trade history cleared ({count} docs deleted).")
    except Exception as e:
        print(f"  Error clearing trade history: {e}")

    print("3. Clearing Vault & Cycles...")
    try:
        db = firebase_service.db
        vault_docs = db.collection("vault_management").stream()
        for doc in vault_docs:
            doc.reference.delete()
        print(f"  Vault documents cleared.")
    except Exception as e:
        print(f"  Error clearing vault: {e}")

    print("4. Resetting Bankroll...")
    try:
        await firebase_service.update_banca_status({
            "configured_balance": 100.0,
            "saldo_total": 100.0,
            "saldo_real_bybit": 0.0,
            "risco_real_percent": 0.0,
            "slots_disponiveis": 4
        })
        print("  Banca reset to $100.00")
    except Exception as e:
        print(f"  Error resetting banca: {e}")
        
    print("Deep Reset Complete!")

if __name__ == "__main__":
    asyncio.run(reset())
