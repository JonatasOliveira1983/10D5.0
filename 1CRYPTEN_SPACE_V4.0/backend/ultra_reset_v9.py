import asyncio
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb

async def main():
    print("--- [ULTRA RESET V9] EMERGENCY PURGE STARTING... ---")
    
    # 1. Local Persistence Wipe (Nuclear)
    files = ["paper_storage.json", "auto_blocks.json", "active_trades.json"]
    for f in files:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"Purged local file: {f}")
            except: pass
    
    # Init clean state with $100.00
    with open("paper_storage.json", "w") as f:
        json.dump({
            "positions": [], 
            "moonbags": [], 
            "balance": 100.0, 
            "history": [],
            "equity": 100.0,
            "cumulative_pnl": 0.0
        }, f, indent=2)

    # 2. Firebase Auth
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app'
            })
        db = firestore.client()
    except Exception as e:
        print(f"Auth error: {e}")
        return

    # 3. Mass Purge: Deep Clean collections with specific focus on slots
    collections = ["trade_history", "banca_history", "slots", "vault", "signals"]
    for coll_name in collections:
        try:
            docs = db.collection(coll_name).get()
            for doc in docs: doc.reference.delete()
            print(f"Collection {coll_name} nuked.")
        except: pass

    # 4. Re-Initialize Active Metrics (V110.12.10)
    db.collection("banca_history").document("status").set({
        "saldo_total": 100.0, 
        "base_capital": 100.0, 
        "configured_balance": 100.0,
        "lucro_acumulado": 0.0,
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    
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

    # Reset Slots with V110.12.10 Status
    for i in range(1, 5):
        db.collection("slots").document(str(i)).set({
            "id": i, 
            "symbol": None, 
            "status_risco": "LIVRE", 
            "pnl_percent": 0.0,
            "entry_price": 0.0, 
            "entry_margin": 0.0, 
            "opened_at": 0,
            "pensamento": "V110.12.10: ATOMIC LOCK ACTIVE - SCANNING TREND"
        })

    # 5. RTDB Wipe (Instant UI Feedback)
    try:
        rtdb.reference("banca_status/status").set({
            "saldo_total": 100.0, 
            "lucro_acumulado": 0.0, 
            "base_capital": 100.0,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        rtdb.reference("trade_history").delete()
        rtdb.reference("active_positions").delete()
    except: pass

    print("--- [ULTRA RESET V9] MISSION COMPLETE: SYSTEM BLINDED & PYTH EVAPORATED ---")

if __name__ == "__main__":
    asyncio.run(main())
