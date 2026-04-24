import asyncio
import os
from google.cloud import firestore
from config import settings
import json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.FIREBASE_CREDENTIALS_PATH

async def surgical_scrub():
    db = firestore.Client()
    
    # 1. Limpar ADAUSDT e PARTIUSDT com PnL bizarro
    print("🔍 Scrubbing ADAUSDT/PARTIUSDT from Firestore...")
    coll = db.collection("trade_history")
    
    # Deletar ADA com lucro de 135
    docs = list(coll.where("symbol", "==", "ADAUSDT").stream())
    for doc in docs:
        d = doc.to_dict()
        if d.get("pnl_usd", 0) > 100:
            print(f"🔥 Deleting anomalous ADA trade: {doc.id} (${d.get('pnl_usd')})")
            doc.reference.delete()

    # Deletar PARTI se houver (o user reclamou tbm)
    docs = list(coll.where("symbol", "==", "PARTIUSDT").stream())
    for doc in docs:
        print(f"🔥 Deleting PARTIUSDT trade: {doc.id}")
        doc.reference.delete()

    # 2. Resetar banca no paper_storage.json e no Firebase
    print("💰 Resetting balance to $100.00...")
    
    # RTDB/Firestore status update
    await db.collection("banca_history").document("status").set({
        "configured_balance": 100.0,
        "saldo_total": 100.0,
        "updated_at": firestore.SERVER_TIMESTAMP
    }, merge=True)

    # Local JSON
    base_dir = os.path.dirname(os.path.abspath(__file__))
    storage_path = os.path.join(base_dir, "paper_storage.json")
    with open(storage_path, 'w') as f:
        json.dump({
            "balance": 100.0,
            "positions": [],
            "history": []
        }, f, indent=2)
        
    print("✅ Scrub and Reset complete.")

if __name__ == "__main__":
    asyncio.run(surgical_scrub())
