import asyncio
import sys
import os

# Adds the backend directory to path so config imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from services.firebase_service import firebase_service

async def wipe_history_only():
    print("Iniciando limpeza APENAS do Historico da Vault e Trade History...")
    await firebase_service.initialize()
    db = firebase_service.db
    if db:
        try:
            # 1. Limpar trade_history
            trades = db.collection("trade_history").stream()
            count_t = 0
            for doc in trades:
                doc.reference.delete()
                count_t += 1
            print(f"OK: {count_t} registros apagados de 'trade_history'.")
        except Exception as e:
            print(f"Erro ao apagar 'trade_history': {e}")
            
        try:
            # 2. Limpar banca_history (vault)
            banca = db.collection("banca_history").stream()
            count_b = 0
            for doc in banca:
                doc.reference.delete()
                count_b += 1
            print(f"OK: {count_b} registros apagados de 'banca_history' (Vault).")
        except Exception as e:
            print(f"Erro ao apagar 'banca_history': {e}")
            
        print("Limpeza concluída! Suas 4 ordens atuais nos Slots permanecem intactas.")
    else:
        print("Erro: Sem conexão ao Firebase.")

if __name__ == "__main__":
    asyncio.run(wipe_history_only())
