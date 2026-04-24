import asyncio
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

async def main():
    cred_path = "c:\\Users\\spcom\\Desktop\\10D-3.0\\1CRYPTEN_SPACE_V4.0\\backend\\serviceAccountKey.json"
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    # 1. Update Vault Management
    vault_ref = db.collection("vault_management").document("current_cycle")
    
    print("Resetting Vault Management...")
    vault_ref.update({
        "cycle_profit": 0.0,
        "cycle_losses": 0.0,
        "cycle_gains_count": 0,
        "cycle_losses_count": 0,
        "total_trades_cycle": 0,
        "used_symbols_in_cycle": [],
        "cycle_start_bankroll": 100.0,
        "mega_cycle_wins": 0,
        "sniper_wins": 0,
        "updated_at": int(datetime.utcnow().timestamp() * 1000),
        "started_at": datetime.utcnow().isoformat()
    })
    print("Vault Reset Confirmed.")

    # 2. Cleanup Corrupted History (Optional but recommended for GALA -240)
    print("Cleaning huge corrupted trades in 'trade_history'...")
    history_docs = db.collection("trade_history").where("symbol", "==", "GALAUSDT").stream()
    for doc in history_docs:
        d = doc.to_dict()
        if abs(d.get("pnl", 0)) > 100:
            print(f"Deleting corrupted GALA trade {doc.id} (PnL: {d.get('pnl')})")
            db.collection("trade_history").document(doc.id).delete()

    print("\n--- RECTIFICATION COMPLETE ---")
    print("Banca master resetada para $100.00")
    print("Prejuízo fantasma de GALA removido.")

if __name__ == "__main__":
    asyncio.run(main())
