import firebase_admin
from firebase_admin import credentials, firestore, db
import json
import os
import asyncio
from datetime import datetime, timezone

# Add backend to path if needed
backend_dir = os.path.dirname(os.path.abspath(__file__))

def full_system_reset():
    print("[FULL-SYSTEM-RESET] Iniciando limpeza total do ecossistema...")
    cert_path = os.path.join(backend_dir, "serviceAccountKey.json")
    if not os.path.exists(cert_path):
        print("Erro: serviceAccountKey.json nao encontrado.")
        return

    # Tenta carregar a URL do RTDB do .env manualmente para evitar problemas de carregamento de config
    rtdb_url = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"
    try:
        with open(os.path.join(backend_dir, ".env"), "r") as f:
            for line in f:
                if "FIREBASE_DATABASE_URL=" in line:
                    rtdb_url = line.split("=")[1].strip()
                    break
    except:
        pass

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(cert_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': rtdb_url
            })
        
        firestore_db = firestore.client()
        
        # RTDB Reset
        try:
            rtdb = db.reference("/")
            print(f"Limpando RTDB em {rtdb_url}...")
            rtdb.child("moonbag_vault").delete()
            rtdb.child("banca_status").set({
                "saldo_total": 100.0,
                "timestamp_last_update": datetime.now().timestamp()
            })
            print("RTDB limpo.")
        except Exception as re:
            print(f"Aviso: Falha ao limpar RTDB: {re}")

        # 1. Reset Banca e Ciclo no Firestore
        print("Resetando Banca para $100 e Ciclo no Firestore...")
        banca_ref = firestore_db.collection("banca_status").document("status")
        banca_ref.set({
            "configured_balance": 100.0,
            "lucro_total_acumulado": 0.0,
            "saldo_total": 100.0,
            "lucro_ciclo": 0.0,
            "vault_total": 0.0,
            "risco_real_percent": 0.0,
            "slots_disponiveis": 4,
            "updated_at": int(datetime.now().timestamp() * 1000)
        })

        vault_ref = firestore_db.collection("vault_management").document("current_cycle")
        vault_ref.set({
            "cycle_start_bankroll": 100.0,
            "cycle_bankroll": 100.0,
            "next_entry_value": 10.0,
            "cycle_profit": 0.0,
            "sniper_wins": 0,
            "total_trades_cycle": 0,
            "cycle_gains_count": 0,
            "cycle_losses_count": 0,
            "mega_cycle_profit": 0.0,
            "mega_cycle_wins": 0,
            "mega_cycle_total": 0,
            "used_symbols_in_cycle": [],
            "started_at": datetime.now(timezone.utc).isoformat()
        })

        # 2. Limpar Slots (Firestore e RTDB)
        print("Limpando todos os 4 Slots...")
        for i in range(1, 5):
            slot_data = {
                "id": i,
                "symbol": None,
                "side": None,
                "status_risco": "LIVRE",
                "pnl_percent": 0,
                "entry_price": 0,
                "current_stop": 0,
                "pensamento": "Sistema Resetado pelo Almirante",
                "timestamp_last_update": datetime.now().timestamp()
            }
            firestore_db.collection("slots_ativos").document(str(i)).set(slot_data)
            try:
                db.reference(f"live_slots/{i}").set(slot_data)
            except:
                pass

        # 3. Limpar Colecoes de Historico e Trades
        collections_to_wipe = ["trade_history", "banca_history", "orders_genesis", "moonbags"]
        for coll_name in collections_to_wipe:
            print(f"Deletando colecao: {coll_name}...")
            coll_ref = firestore_db.collection(coll_name)
            docs = coll_ref.stream()
            count = 0
            for doc in docs:
                doc.reference.delete()
                count += 1
            print(f"   - {count} documentos removidos de {coll_name}.")

        # 5. Limpar paper_storage.json local
        paper_path = os.path.join(backend_dir, "paper_storage.json")
        if os.path.exists(paper_path):
            print("Resetando paper_storage.json...")
            empty_data = {
                "balance": 100.0,
                "positions": [],
                "history": [],
                "moonbags": [],
                "updated_at": int(datetime.now().timestamp() * 1000)
            }
            with open(paper_path, 'w') as f:
                json.dump(empty_data, f, indent=2)

        print("\n[RESET-COMPLETE] Sistema resetado com sucesso para o Estado Zero.")
        print("Banca: $100.00 | Slots: Livres | Historico: Limpo.")

    except Exception as e:
        print(f"Erro fatal durante o reset: {e}")

if __name__ == "__main__":
    full_system_reset()
