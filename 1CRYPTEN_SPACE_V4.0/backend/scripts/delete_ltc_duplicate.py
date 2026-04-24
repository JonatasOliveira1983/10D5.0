
import asyncio
from services.sovereign_service import sovereign_service

async def delete_duplicate():
    await sovereign_service.initialize()
    doc_id = "u8UjoMi1mTDjfvu6JXTo"
    print(f"🔥 Deletando duplicata: {doc_id}...")
    sovereign_service.db.collection("trade_history").document(doc_id).delete()
    print("✅ Sucesso!")

if __name__ == "__main__":
    asyncio.run(delete_duplicate())
