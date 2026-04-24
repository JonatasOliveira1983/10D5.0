import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sovereign_service import sovereign_service
from google.cloud import firestore

async def nuke_slots():
    print("🔥 NUKING ALL GHOST POSITIONS 🔥")
    await sovereign_service.initialize()
    
    db = sovereign_service.db
    rtdb = sovereign_service.rtdb

    # 1. Nuke Firestore slots_ativos
    print("Nuking Firestore slots_ativos...")
    for i in range(1, 5):
        try:
            doc_ref = db.collection("slots_ativos").document(str(i))
            # Delete first to wipe any hidden weird fields
            await asyncio.to_thread(doc_ref.delete)
            # Recreate cleanly
            await asyncio.to_thread(doc_ref.set, {
                "id": i,
                "symbol": "",  # Empty string explicit rather than None
                "status_risco": "IDLE",
                "entry_price": 0,
                "current_stop": 0,
                "target_price": 0,
                "pnl_percent": 0,
                "qty": 0,
                "side": "",
                "pensamento": "Nuked by admin"
            })
            print(f"✅ Firestore Slot {i} completely wiped and recreated.")
        except Exception as e:
            print(f"❌ Error nuking Firestore slot {i}: {e}")

    # 2. Nuke RTDB live_slots
    print("\nNuking RTDB live_slots...")
    if rtdb:
        for i in range(1, 5):
            try:
                # Set directly explicitly
                await asyncio.to_thread(rtdb.child("live_slots").child(str(i)).set, {
                    "id": i,
                    "symbol": "",
                    "status_risco": "IDLE",
                    "entry_price": 0,
                    "current_stop": 0,
                    "target_price": 0,
                    "pnl_percent": 0,
                    "qty": 0,
                    "side": "",
                    "pensamento": "Nuked by admin"
                })
                print(f"✅ RTDB live_slots {i} overwritten cleanly.")
            except Exception as e:
                print(f"❌ Error nuking RTDB slot {i}: {e}")
        
        try:
            await asyncio.to_thread(rtdb.child("banca_status").child("slots").delete)
            print("✅ RTDB banca_status/slots deleted completely.")
        except: pass

    # 3. Clean paper_storage.json one more time locally
    import json
    try:
        with open("paper_storage.json", "w") as f:
            json.dump({"positions": [], "balance": 100.0, "history": []}, f, indent=2)
        print("✅ Local paper_storage.json erased.")
    except: pass
    
    print("\n💀 Nuke Operation Complete. All layers sanitized.")

if __name__ == "__main__":
    asyncio.run(nuke_slots())
