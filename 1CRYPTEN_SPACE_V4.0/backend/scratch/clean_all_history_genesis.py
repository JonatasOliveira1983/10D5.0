import asyncio
import sys
import os

# Adds the backend directory to path so config imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from services.firebase_service import firebase_service

async def wipe_all_history_and_genesis():
    print("Iniciando limpeza total do Historico (Trade, Banca e Genesis)...")
    await firebase_service.initialize()
    db = firebase_service.db
    if db:
        collections_to_wipe = ["trade_history", "banca_history", "orders_genesis"]
        
        for coll_name in collections_to_wipe:
            try:
                docs = db.collection(coll_name).stream()
                count = 0
                for doc in docs:
                    doc.reference.delete()
                    count += 1
                print(f"OK: {count} registros apagados de '{coll_name}'.")
            except Exception as e:
                print(f"Erro ao apagar '{coll_name}': {e}")
                
        print("Limpeza concluída! Todo o lixo histórico foi deletado.")
    else:
        print("Erro: Sem conexão ao Firebase.")

if __name__ == "__main__":
    asyncio.run(wipe_all_history_and_genesis())
