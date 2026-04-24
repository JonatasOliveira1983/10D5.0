import asyncio
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb

async def main():
    print("--- [ULTRA RESET V8] NUCLEAR PURGE STARTING... ---")
    
    # 1. Local Persistence Wipe
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

    # 3. Mass Purge
    collections = ["trade_history", "banca_history", "slots", "vault", "signals"]
    for coll_name in collections:
        try:
            docs = db.collection(coll_name).get()
            for doc in docs: doc.reference.delete()
            print(f"Collection {coll_name} nuked.")
        except: pass

    # 4. Re-Initialize Active Metrics
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

    for i in range(1, 5):
        db.collection("slots").document(str(i)).set({
            "id": i, 
            "symbol": None, 
            "status_risco": "LIVRE", 
            "pnl_percent": 0.0,
            "entry_price": 0.0, 
            "entry_margin": 0.0, 
            "pensamento": "V110.12.9: PROTOCOLO GUARDIÃO ATIVO - AGUARDANDO TREND"
        })

    # 5. RTDB Wipe
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

    print("--- [ULTRA RESET V8] MISSION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
