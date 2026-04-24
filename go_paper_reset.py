# -*- coding: utf-8 -*-
"""
GO PAPER RESET V1.0
======================
Script de transicao REAL -> PAPER.
Limpa todos os dados historicos e inicializa o sistema
para operacao PAPER com banca de $20.
"""
import firebase_admin
from firebase_admin import credentials, firestore, db
import os
from datetime import datetime, timezone

PAPER_BANKROLL = 100.0  # $100 Banca Paper
LEVERAGE = 50

def go_paper_reset():
    print("=" * 60)
    print("GO PAPER RESET V1.0 - Transicao REAL -> PAPER")
    print("=" * 60)
    print(f"Time (UTC): {datetime.now(timezone.utc).isoformat()}")
    print(f"Bankroll: ${PAPER_BANKROLL:.2f}")
    print(f"Margin per Order: ${PAPER_BANKROLL * 0.10:.2f} (10%)")
    print(f"Leverage: {LEVERAGE}x")
    print("=" * 60)
    
    cert_path = "1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
    if not os.path.exists(cert_path):
        print("Error: Credentials not found at " + cert_path)
        return

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(cert_path)
            database_url = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
        
        firestore_db = firestore.client()
        rtdb = db.reference()

        # 1. DELETE Trade History (Firestore)
        print("\n1/8 Deletando trade_history...")
        try:
            trades = firestore_db.collection("trade_history").limit(500).stream()
            count = 0
            for doc in trades:
                doc.reference.delete()
                count += 1
            print(f"   Success: {count} trades deletados.")
        except Exception as e:
            print(f"   Error: {e}")

        # 2. DELETE Trade Analytics (Firestore)
        print("\n2/8 Deletando trade_analytics...")
        try:
            analytics = firestore_db.collection("trade_analytics").limit(500).stream()
            count = 0
            for doc in analytics:
                doc.reference.delete()
                count += 1
            print(f"   Success: {count} documentos deletados.")
        except Exception as e:
            print(f"   Error: {e}")

        # 3. RESET Slots 1-4 (Firestore)
        print("\n3/8 Resetando Slots 1-4...")
        reset_slot = {
            "symbol": None,
            "side": None,
            "entry_price": 0,
            "current_stop": 0,
            "target_price": None,
            "status_risco": "LIVRE",
            "pnl_percent": 0,
            "slot_type": None,
            "pensamento": "GO PAPER V1.0: Slot limpo para operacao paper",
            "visual_status": "IDLE",
            "entry_margin": 0,
            "qty": 0,
            "pattern": None,
            "leverage": LEVERAGE
        }
        for i in range(1, 5):
            firestore_db.collection("slots_ativos").document(str(i)).set(reset_slot)
        print("   Success: Slots 1-4 resetados para LIVRE.")

        # 4. RESET Banca Status (Firestore)
        print("\n4/8 Configurando banca_status com $20 paper...")
        banca_data = {
            "id": "status",
            "configured_balance": PAPER_BANKROLL,
            "saldo_real_bybit": 0,
            "saldo_total": PAPER_BANKROLL,
            "risco_real_percent": 0,
            "slots_disponiveis": 4,
            "lucro_total_acumulado": 0,
            "lucro_ciclo": 0,
            "vault_total": 0,
            "leverage": LEVERAGE
        }
        firestore_db.collection("banca_status").document("status").set(banca_data)
        print(f"   Success: banca_status configurado: ${PAPER_BANKROLL:.2f}")

        # 5. RESET Vault Cycle (Firestore)
        print("\n5/8 Resetando vault_management/current_cycle...")
        vault_cycle_data = {
            "cycle_number": 1,
            "mega_cycle_number": 1,
            "mega_cycle_wins": 0,
            "mega_cycle_total": 0,
            "mega_cycle_profit": 0.0,
            "cycle_start_bankroll": PAPER_BANKROLL,
            "cycle_bankroll": PAPER_BANKROLL,
            "cycle_profit": 0.0,
            "cycle_losses": 0.0,
            "total_trades_cycle": 0,
            "cycle_gains_count": 0,
            "cycle_losses_count": 0,
            "sniper_wins": 0,
            "used_symbols_in_cycle": [],
            "min_score_threshold": 60,
            "sniper_mode_active": True,
            "in_admiral_rest": False,
            "rest_until": None,
            "vault_total": 0.0,
            "cautious_mode": False,
            "accumulated_vault": 0.0,
            "next_entry_value": PAPER_BANKROLL * 0.10,
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        firestore_db.collection("vault_management").document("current_cycle").set(vault_cycle_data)
        print(f"   Success: Vault Cycle #1 iniciado.")

        # 6. CLEAR RTDB Nodes
        print("\n6/8 Limpando nodes RTDB...")
        nodes_to_clear = ["radar_pulse", "live_slots", "market_radar", "system_state", "vault_status", "chat_status"]
        for node in nodes_to_clear:
            try:
                rtdb.child(node).delete()
            except:
                pass
        print("   Success: RTDB nodes limpos.")

        # 7. RE-INITIALIZE RTDB Live Slots
        print("\n7/8 Inicializando live_slots no RTDB...")
        rtdb_slots = {str(i): reset_slot for i in range(1, 5)}
        rtdb.child("live_slots").set(rtdb_slots)
        print("   Success: live_slots 1-4 inicializados.")

        # 8. RE-INITIALIZE RTDB Vault Status
        print("\n8/8 Inicializando vault_status no RTDB...")
        rtdb.child("vault_status").set({
            "cycle_number": 1,
            "mega_cycle_number": 1,
            "mega_cycle_wins": 0,
            "cycle_start_bankroll": PAPER_BANKROLL,
            "cycle_profit": 0.0,
            "total_trades_cycle": 0,
            "sniper_wins": 0,
            "used_symbols_in_cycle": [],
            "sniper_mode_active": True,
            "in_admiral_rest": False
        })
        print(f"   Success: vault_status inicializado.")

        print("\n" + "=" * 60)
        print("GO PAPER RESET COMPLETED!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    go_paper_reset()
