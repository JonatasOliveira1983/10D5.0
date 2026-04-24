import os
import json
import asyncio
from datetime import datetime, timezone

# Ajusta o path para importar os serviços se necessário
import sys
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

async def surgical_reset():
    print("[V110.45] Iniciando Reset Cirurgico de Banca e Historico...")
    
    # Importa serviços após ajuste de path
    from services.sovereign_service import sovereign_service
    await sovereign_service.initialize()
    
    if not sovereign_service.is_active:
        print("ERROR: Firebase nao pode ser inicializado. Abortando.")
        return

    db = sovereign_service.db
    rtdb = sovereign_service.rtdb

    try:
        # 1. LIMPEZA DE COLEÇÕES (Histórico)
        print("CLEANING Limpando colecoes de historico...")
        # trade_history
        trade_docs = db.collection("trade_history").stream()
        count_t = 0
        for doc in trade_docs:
            doc.reference.delete()
            count_t += 1
        print(f"OK: {count_t} registros removidos de 'trade_history'.")

        # banca_history
        banca_docs = db.collection("banca_history").stream()
        count_b = 0
        for doc in banca_docs:
            doc.reference.delete()
            count_b += 1
        print(f"OK: {count_b} registros removidos de 'banca_history'.")

        # 2. RESET DE STATUS (Banca)
        print("RESET Resetando documentos de status para $100...")
        banca_data = {
            "configured_balance": 100.0,
            "lucro_total_acumulado": 0.0,
            "saldo_total": 100.0,
            "lucro_ciclo": 0.0,
            "vault_total": 0.0,
            "updated_at": int(datetime.now().timestamp() * 1000)
        }
        db.collection("banca_status").document("status").set(banca_data, merge=True)
        if rtdb:
            rtdb.child("banca_status").set(banca_data)
        print("OK: 'banca_status/status' resetado.")

        # 3. RESET DE VAULT MANAGEMENT
        print("VAULT Resetando vault_management/current_cycle...")
        vault_data = {
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
        }
        db.collection("vault_management").document("current_cycle").set(vault_data, merge=True)
        print("OK: 'vault_management/current_cycle' resetado.")

        # 4. SINCRONIZAÇÃO PAPER STORAGE LOCAL
        print("FILE Ajustando paper_storage.json (Preservando Slots)...")
        paper_path = os.path.join(backend_dir, "paper_storage.json")
        if os.path.exists(paper_path):
            with open(paper_path, 'r') as f:
                data = json.load(f)
            
            # Resetamos saldo e histórico, mas MANTEMOS positions
            data["balance"] = 100.0
            data["history"] = []
            
            with open(paper_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"OK: 'paper_storage.json' atualizado. Saldo: ${data['balance']}. Posicoes preservadas: {len(data.get('positions', []))}")

        # 5. VERIFICAÇÃO DE SLOTS (Segurança)
        slots = await sovereign_service.get_active_slots(force_refresh=True)
        active_symbols = [s.get('symbol') for s in slots if s.get('symbol')]
        print(f"STATUS FINAL DOS SLOTS: {active_symbols}")
        if len(active_symbols) >= 3:
            print("SUCCESS! As 3 ordens permanecem ativas conforme solicitado.")
        else:
            print("WARNING: Detectados menos de 3 slots ativos. Verifique o Dashboard.")

        print("SUCCESS! RESET CIRURGICO CONCLUIDO COM SUCESSO!")

    except Exception as e:
        print(f"FATAL ERROR DURING RESET: {e}")
        # import traceback
        # traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(surgical_reset())
