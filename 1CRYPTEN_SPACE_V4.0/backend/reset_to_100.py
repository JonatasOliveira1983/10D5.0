import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime, timezone

def surgical_bankroll_reset():
    print("Iniciando Reset Cirurgico da Banca e Vault (V110.5)...")
    cert_path = "serviceAccountKey.json"
    if not os.path.exists(cert_path):
        print("Erro: Credenciais nao encontradas.")
        return

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(cert_path)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        # 1. Reset banca_status/status
        print("Resetando banca_status/status...")
        banca_ref = db.collection("banca_status").document("status")
        banca_ref.update({
            "configured_balance": 100.0,
            "lucro_total_acumulado": 0.0,
            "saldo_total": 100.0,
            "lucro_ciclo": 0.0,
            "vault_total": 0.0,
            "updated_at": int(datetime.now().timestamp() * 1000)
        })

        # 2. Reset vault_management/current_cycle
        print("Resetando vault_management/current_cycle (Casco)...")
        vault_ref = db.collection("vault_management").document("current_cycle")
        vault_ref.update({
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

        # 3. Reset paper_storage.json local (Simulacao)
        print("Sincronizando paper_storage.json...")
        paper_path = "paper_storage.json"
        if os.path.exists(paper_path):
            with open(paper_path, 'r') as f:
                data = json.load(f)
            
            data["balance"] = 100.0
            data["positions"] = [] 
            data["history"] = []   
            data["moonbags"] = []
            
            with open(paper_path, 'w') as f:
                json.dump(data, f, indent=2)
            print("paper_storage.json resetado para $100.")

        # 4. Limpar trade_history
        print("Limpando historico de trades para PnL 0...")
        history_ref = db.collection("trade_history")
        docs = history_ref.stream()
        count = 0
        for doc in docs:
            doc.reference.delete()
            count += 1
        print(f"{count} registros de historico removidos.")

        print("\nRESET CONCLUIDO COM SUCESSO!")
        print("UI deve mostrar Dinheiro Base $100 e Patrimônio Total $100.")

    except Exception as e:
        print(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    surgical_bankroll_reset()
