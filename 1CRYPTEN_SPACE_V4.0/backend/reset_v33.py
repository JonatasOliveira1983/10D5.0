import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.firebase_service import firebase_service
from services.vault_service import vault_service

async def reset_v33():
    print("=== V33.0 CLEAN RESET ===")
    await firebase_service.initialize()
    
    print("1. Clearing Trade History...")
    try:
        db = firebase_service.db
        trades = db.collection("trade_history").limit(500).stream()
        count = 0
        for doc in trades:
            doc.reference.delete()
            count += 1
        print(f"   {count} trade history docs deleted.")
    except Exception as e:
        print(f"   Error: {e}")

    print("2. Clearing Vault & Cycles...")
    try:
        db = firebase_service.db
        vault_docs = db.collection("vault_management").stream()
        v_count = 0
        for doc in vault_docs:
            doc.reference.delete()
            v_count += 1
        print(f"   {v_count} vault docs deleted.")
    except Exception as e:
        print(f"   Error: {e}")

    print("3. Clearing Signal History...")
    try:
        db = firebase_service.db
        signals = db.collection("signal_history").limit(500).stream()
        s_count = 0
        for doc in signals:
            doc.reference.delete()
            s_count += 1
        print(f"   {s_count} signal docs deleted.")
    except Exception as e:
        print(f"   Error: {e}")

    print("4. Clearing RTDB slots + cooldowns...")
    try:
        if firebase_service.rtdb:
            firebase_service.rtdb.child("slots").delete()
            firebase_service.rtdb.child("cooldowns").delete()
            firebase_service.rtdb.child("analytics").delete()
            print("   RTDB slots, cooldowns, analytics cleared.")
    except Exception as e:
        print(f"   Error: {e}")

    print("5. Resetting Banca to $10.00...")
    try:
        await firebase_service.update_banca_status({
            "configured_balance": 100.0,
            "saldo_total": 100.0,
            "saldo_real_bybit": 0.0,
            "risco_real_percent": 0.0,
            "slots_disponiveis": 4,
            "lucro_total_acumulado": 0.0,
            "lucro_ciclo": 0.0,
            "vault_total": 0.0
        })
        print("   Banca reset to $10.00")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n=== V33.0 CLEAN RESET COMPLETE ===")
    print("Sistema pronto para teste limpo com V33.0!")

if __name__ == "__main__":
    asyncio.run(reset_v33())
