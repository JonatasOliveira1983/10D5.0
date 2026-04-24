
import asyncio
from services.firebase_service import firebase_service

async def delete_duplicate():
    await firebase_service.initialize()
    doc_id = "u8UjoMi1mTDjfvu6JXTo"
    print(f"🔥 Deletando duplicata: {doc_id}...")
    firebase_service.db.collection("trade_history").document(doc_id).delete()
    print("✅ Sucesso!")

if __name__ == "__main__":
    asyncio.run(delete_duplicate())
