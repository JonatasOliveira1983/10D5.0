import asyncio
import os
import sys
import time
import logging

# Adiciona o diretório backend ao path para importar os serviços
sys.path.append(os.getcwd())

from services.firebase_service import firebase_service
from services.bankroll import BankrollManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepNuke")

async def run_deep_nuke():
    print("[DEEP NUKE] Iniciando limpeza PROFUNDA e ABSOLUTA...")
    
    # 1. Inicializa Firebase
    await firebase_service.initialize()
    if not firebase_service.is_active:
        print("FAIL: Falha ao conectar ao Firebase.")
        return

    # 2. Reset de Banca Status (Firestore + RTDB)
    print("BANKROLL: Resetando banca para $100.00...")
    reset_data = {
        "configured_balance": 100.0,
        "saldo_total": 100.0,
        "lucro_ciclo": 0.0,
        "lucro_total_acumulado": 0.0,
        "vault_total": 0.0,
        "risco_real_percent": 0.0,
        "slots_disponiveis": 4,
        "status": "ONLINE",
        "timestamp_last_update": time.time()
    }
    await asyncio.to_thread(firebase_service.db.collection("banca_status").document("status").set, reset_data)
    if firebase_service.rtdb:
        await asyncio.to_thread(firebase_service.rtdb.child("banca_status").set, reset_data)
    print("SUCCESS: Banca resetada.")

    # 3. Limpeza de Coleções Firestore (Todos os documentos)
    collections_to_wipe = ["slots_ativos", "moonbags", "orders_genesis", "trade_history", "banca_history"]
    for coll_name in collections_to_wipe:
        print(f"FIRESTORE: Limpando colecao {coll_name}...")
        try:
            docs = firebase_service.db.collection(coll_name).limit(500).stream()
            count = 0
            for doc in docs:
                await asyncio.to_thread(doc.reference.delete)
                count += 1
            print(f"SUCCESS: {count} documentos deletados de {coll_name}.")
        except Exception as e:
            print(f"ERROR: Falha ao limpar {coll_name}: {e}")

    # 4. Limpeza Nuclear do Realtime Database (Nós Raiz)
    if firebase_service.rtdb:
        nodes_to_wipe = ["live_slots", "moonbag_vault", "system_pulse", "radar_pulse", "agent_logs"]
        for node in nodes_to_wipe:
            print(f"RTDB: Deletando no raiz {node}...")
            try:
                await asyncio.to_thread(firebase_service.rtdb.child(node).delete)
                print(f"SUCCESS: No {node} deletado do RTDB.")
            except Exception as e:
                print(f"ERROR: Falha ao deletar no {node}: {e}")
    else:
        print("SKIP: RTDB nao conectado.")

    print("\nFINISH: [DEEP NUKE COMPLETE] O sistema esta em estado puro (GENESIS).")

if __name__ == "__main__":
    asyncio.run(run_deep_nuke())
