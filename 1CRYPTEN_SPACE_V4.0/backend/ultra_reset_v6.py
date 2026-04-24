import asyncio
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb

async def main():
    print("--- [ULTRA RESET V6] STARTING... ---")
    
    # 1. Local Files
    files = ["paper_storage.json", "auto_blocks.json"]
    for f in files:
        if os.path.exists(f):
            os.remove(f)
            print(f"File removed: {f}")
    
    # Init blank paper storage
    with open("paper_storage.json", "w") as f:
        json.dump({"positions": [], "moonbags": [], "balance": 100.0, "history": []}, f, indent=2)
        print("Initialized empty paper_storage.json at $100.00")

    # 2. Firebase Auth
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app'
            })
        db = firestore.client()
        print("Firebase Auth Success.")
    except Exception as e:
        print(f"Auth Fail: {e}")
        return

    # 3. Clean Firestore History
    try:
        docs = db.collection("trade_history").get()
        for doc in docs: doc.reference.delete()
        print("trade_history cleaned.")
    except Exception as e: print(f"Trade hist error: {e}")

    # 4. Reset ALL Balance Collections (Firestore)
    try:
        # banca_history/status (The UI probably uses this)
        db.collection("banca_history").document("status").set({
            "saldo_total": 100.0,
            "base_capital": 100.0,
            "configured_balance": 100.0,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        
        # config/banca
        db.collection("config").document("banca").set({
            "saldo_total": 100.0,
            "base_capital": 100.0,
            "lucro_acumulado": 0.0,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        
        # vault_management/current_cycle
        db.collection("vault_management").document("current_cycle").set({
            "cycle_number": 1,
            "sniper_wins": 0,
            "cycle_profit": 0.0,
            "cycle_losses": 0.0,
            "cycle_bankroll": 100.0,
            "cycle_start_bankroll": 100.0,
            "next_entry_value": 10.0,
            "vault_total": 0.0,
            "order_ids_processed": [],
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        print("All Firestore balance anchors reset to $100.00")
    except Exception as e: print(f"Firestore balance error: {e}")

    # 5. Clear Slots
    try:
        for i in range(1, 5):
            db.collection("slots").document(str(i)).set({
                "id": i,
                "symbol": None,
                "status_risco": "LIVRE",
                "pnl_percent": 0.0,
                "entry_price": 0.0,
                "entry_margin": 0.0,
                "pensamento": "SYSTEM_REBOOT: V110.12.7 ENFORCED"
            })
        print("4/4 Slots cleared.")
    except Exception as e: print(f"Slot error: {e}")

    # 6. RTDB Reset
    try:
        import time
        rtdb.reference("banca_status/status").set({
            "saldo_total": 100.0,
            "lucro_acumulado": 0.0,
            "base_capital": 100.0,
            "updated_at": int(time.time() * 1000)
        })
        rtdb.reference("trade_history").delete()
        print("RTDB Balance/History reset.")
    except Exception as e: print(f"RTDB error: {e}")

    print("--- [ULTRA RESET V6] COMPLETE! ---")

if __name__ == "__main__":
    asyncio.run(main())
