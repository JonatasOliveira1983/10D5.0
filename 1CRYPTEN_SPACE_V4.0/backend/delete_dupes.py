
import asyncio
import os
import sys

# Adicionar o caminho do backend para importar os serviços
sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))

from services.firebase_service import FirebaseService

async def delete_duplicates():
    fs = FirebaseService()
    await fs.initialize()
    
    # IDs das duplicatas identificadas
    ids_to_delete = [
        "paper_GUNUSDT_1774094522.0572333",
        "paper_AKTUSDT_1774090136.4228358",
        "paper_AKTUSDT_1774089905.1023629"
    ]
    
    print(f"Starting deletion of {len(ids_to_delete)} duplicates...")
    
    for doc_id in ids_to_delete:
        try:
            # Deletar do Firestore
            # fs.db.collection("trade_history").document(doc_id).delete()
            # Precisamos usar a thread para evitar bloqueio e garantir compatibilidade com as APIs do Firebase
            await asyncio.to_thread(fs.db.collection("trade_history").document(doc_id).delete)
            print(f"SUCCESS Deleted: {doc_id}")
        except Exception as e:
            print(f"ERROR Failed to delete {doc_id}: {e}")

    print("Cleanup complete.")

if __name__ == "__main__":
    asyncio.run(delete_duplicates())
