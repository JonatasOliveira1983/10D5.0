import asyncio
import os
import sys
import datetime
from firebase_admin import credentials, firestore, db as rtdb_admin
import firebase_admin

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from services.sovereign_service import sovereign_service
from config import settings

async def surgical_reset():
    print("--- Iniciando RESET CIRURGICO (Clean Start V6.5) ---")
    
    # Force Absolute Path for Credentials
    cred_path = os.path.join(current_dir, "serviceAccountKey.json")
    if not os.path.exists(cred_path):
        print(f"[X] Arquivo de credenciais nao encontrado em: {cred_path}")
        return

    try:
        print("--- Inicializando Firebase manualmente...")
        try:
            firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate(cred_path)
            options = {'databaseURL': settings.FIREBASE_DATABASE_URL}
            firebase_admin.initialize_app(cred, options)
        
        sovereign_service.db = firestore.client()
        sovereign_service.rtdb = rtdb_admin.reference("/")
        sovereign_service.is_active = True
        print("--- Firebase conectado com sucesso!")
    except Exception as e:
        print(f"[X] Falha na conexao: {e}")
        return

    # 1. Limpeza de Slots (Firestore & RTDB)
    print("--- Limpando slots de operacao (1-4) ---")
    for i in range(1, 5):
        await sovereign_service.free_slot(i, reason="SURGICAL RESET - CLEAN START V6.5")
    
    # 2. Reset de Banca (Firestore & RTDB)
    print("--- Resetando banca para $100.00 ---")
    banca_data = {
        "saldo_total": 100.00,
        "configured_balance": 100.00,
        "lucro_total_acumulado": 0.0,
        "slots_disponiveis": 4,
        "risco_real_percent": 0.0,
        "status": "SCANNING",
        "last_update": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    await sovereign_service.update_banca_status(banca_data)

    # 3. Limpeza de Historicos (Firestore)
    collections_to_clear = ["trade_history", "banca_history", "journey_signals", "system_logs"]
    for coll in collections_to_clear:
        print(f"--- Limpando colecao Firestore: {coll} ---")
        try:
            # Delete in batches to avoid timeout
            docs = sovereign_service.db.collection(coll).limit(100).stream()
            deleted_total = 0
            while True:
                batch = sovereign_service.db.batch()
                count = 0
                docs_list = list(docs)
                if not docs_list:
                    break
                for doc in docs_list:
                    batch.delete(doc.reference)
                    count += 1
                batch.commit()
                deleted_total += count
                print(f"   -> Removidos {deleted_total} documentos...")
                docs = sovereign_service.db.collection(coll).limit(100).stream()
            print(f"   -> Total: {deleted_total} documentos removidos de {coll}.")
        except Exception as e:
            print(f"   -> Erro ao limpar {coll}: {e}")

    # 4. Limpeza de RTDB (Nodes em tempo real)
    if sovereign_service.rtdb:
        nodes_to_clear = ["live_slots", "radar_pulse", "historico_trades", "system_logs"]
        for node in nodes_to_clear:
            print(f"--- Limpando node RTDB: {node} ---")
            sovereign_service.rtdb.child(node).delete()
            
    print("\n--- RESET CIRURGICO COMPLETO ---")
    print("--- Sistema pronto para novo ciclo com Sentinel corrigido ---")

if __name__ == "__main__":
    asyncio.run(surgical_reset())
