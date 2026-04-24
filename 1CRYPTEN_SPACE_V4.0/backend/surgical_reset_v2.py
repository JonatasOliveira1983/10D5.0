import asyncio
import os
import sys
import json

# Ensure backend module can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.firebase_service import firebase_service

async def surgical_reset():
    print("🚀 Starting SURGICAL RESET V2.0...")
    await firebase_service.initialize()
    
    # 1. Reset Slots to IDLE
    print("1. Clearing Slots 1 to 4...")
    empty_slot = {
        "symbol": None, "entry_price": 0, "current_stop": 0, "entry_margin": 0,
        "status_risco": "IDLE", "side": None, "pnl_percent": 0, "target_price": 0,
        "qty": 0, "slot_type": None, "pattern": None, "pensamento": ""
    }
    for i in range(1, 5):
        try:
            await firebase_service.update_slot(i, empty_slot)
            print(f"  ✅ Slot {i} cleared.")
        except Exception as e:
            print(f"  ❌ Error slot {i}: {e}")

    # 2. Clear Collections (History, Vault, Signals)
    collections_to_clear = ["trade_history", "vault_management", "signals", "radar_pulse"]
    print(f"2. Clearing Firestore Collections: {collections_to_clear}...")
    db = firebase_service.db
    for coll_name in collections_to_clear:
        try:
            docs = db.collection(coll_name).limit(500).stream()
            count = 0
            for doc in docs:
                doc.reference.delete()
                count += 1
            print(f"  ✅ {coll_name} cleared ({count} docs).")
        except Exception as e:
            print(f"  ❌ Error clearing {coll_name}: {e}")

    # 3. Reset Banca in Firestore
    print("3. Resetting Banca Status to $100.00...")
    try:
        await firebase_service.update_banca_status({
            "configured_balance": 100.0,
            "saldo_total": 100.0,
            "saldo_real_bybit": 0.0,
            "risco_real_percent": 0.0,
            "slots_disponiveis": 4,
            "lucro_total_acumulado": 0.0
        })
        print("  ✅ Firestore Banca reset.")
    except Exception as e:
        print(f"  ❌ Error resetting banca: {e}")

    # 4. Reset paper_storage.json
    print("4. Resetting paper_storage.json...")
    try:
        paper_path = "paper_storage.json"
        initial_paper = {
            "positions": [],
            "balance": 100.0,
            "history": []
        }
        with open(paper_path, "w") as f:
            json.dump(initial_paper, f, indent=2)
        print("  ✅ local paper_storage.json reset.")
    except Exception as e:
        print(f"  ❌ Error resetting paper_storage: {e}")

    # 5. Reset RTDB Vault status
    if firebase_service.rtdb:
        print("5. Resetting RTDB Vault Status...")
        try:
            firebase_service.rtdb.child("vault_status").set({
                "cycle_profit": 0,
                "vault_total": 0,
                "updated_at": 0
            })
            print("  ✅ RTDB Vault reset.")
        except Exception as e:
            print(f"  ❌ Error resetting RTDB: {e}")

    print("\n✨ SURGICAL RESET COMPLETE. System ready for $100 run.")

if __name__ == "__main__":
    asyncio.run(surgical_reset())
