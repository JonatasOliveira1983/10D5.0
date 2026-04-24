# -*- coding: utf-8 -*-
"""
🔴 GO REAL RESET V26.0
======================
Script de transição PAPER → REAL.
Limpa todos os dados históricos do modo PAPER e inicializa o sistema
para operação REAL com banca de $10.

ATENÇÃO: Este script DELETA permanentemente:
- trade_history (Firestore)
- trade_analytics (Firestore)
- banca_status (Firestore) → reinicializado com $10
- vault_management/current_cycle (Firestore) → reinicializado
- slots_ativos 1-4 (Firestore) → resetados para IDLE
- RTDB nodes: radar_pulse, live_slots, market_radar, system_state, vault_status
"""
import firebase_admin
from firebase_admin import credentials, firestore, db
import os
from datetime import datetime, timezone

REAL_BANKROLL = 10.0  # $10 Banca Real
LEVERAGE = 50

def go_real_reset():
    print("=" * 60)
    print("🔴 GO REAL RESET V26.0 — Transição PAPER → REAL")
    print("=" * 60)
    print(f"⏰ {datetime.now(timezone.utc).isoformat()}")
    print(f"💰 Banca Real: ${REAL_BANKROLL:.2f}")
    print(f"📊 Margem por Ordem: ${REAL_BANKROLL * 0.10:.2f} (10%)")
    print(f"⚡ Leverage: {LEVERAGE}x")
    print("=" * 60)
    
    cert_path = "1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
    if not os.path.exists(cert_path):
        print("❌ Error: Credentials not found at", cert_path)
        return

    try:
        cred = credentials.Certificate(cert_path)
        database_url = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"
        
        firebase_admin.initialize_app(cred, {
            'databaseURL': database_url
        })
        
        firestore_db = firestore.client()
        rtdb = db.reference()

        # ============================================================
        # 1. DELETE Trade History (Firestore)
        # ============================================================
        print("\n📋 1/8 Deletando trade_history...")
        try:
            trades = firestore_db.collection("trade_history").limit(500).stream()
            count = 0
            for doc in trades:
                doc.reference.delete()
                count += 1
            print(f"   ✅ {count} trades deletados do histórico.")
        except Exception as e:
            print(f"   ⚠️ Erro ao limpar trade_history: {e}")

        # ============================================================
        # 2. DELETE Trade Analytics (Firestore)
        # ============================================================
        print("\n📊 2/8 Deletando trade_analytics...")
        try:
            analytics = firestore_db.collection("trade_analytics").limit(500).stream()
            count = 0
            for doc in analytics:
                doc.reference.delete()
                count += 1
            print(f"   ✅ {count} documentos de analytics deletados.")
        except Exception as e:
            print(f"   ⚠️ Erro ao limpar trade_analytics: {e}")

        # ============================================================
        # 3. RESET Slots 1-4 (Firestore)
        # ============================================================
        print("\n🎰 3/8 Resetando Slots 1-4...")
        reset_slot = {
            "symbol": None,
            "side": None,
            "entry_price": 0,
            "current_stop": 0,
            "target_price": None,
            "status_risco": "LIVRE",
            "pnl_percent": 0,
            "slot_type": None,
            "pensamento": "GO REAL V26.0: Slot limpo para operação real",
            "visual_status": "IDLE",
            "entry_margin": 0,
            "qty": 0,
            "pattern": None,
            "leverage": LEVERAGE
        }
        for i in range(1, 5):
            firestore_db.collection("slots_ativos").document(str(i)).set(reset_slot)
        print("   ✅ Slots 1-4 resetados para IDLE.")

        # ============================================================
        # 4. RESET Banca Status (Firestore)
        # ============================================================
        print("\n💰 4/8 Configurando banca_status com $10 real...")
        banca_data = {
            "id": "status",
            "configured_balance": REAL_BANKROLL,
            "saldo_real_bybit": REAL_BANKROLL,
            "saldo_total": REAL_BANKROLL,
            "risco_real_percent": 0,
            "slots_disponiveis": 4,
            "lucro_total_acumulado": 0,
            "lucro_ciclo": 0,
            "vault_total": 0,
            "leverage": LEVERAGE
        }
        firestore_db.collection("banca_status").document("status").set(banca_data)
        print(f"   ✅ banca_status configurado: ${REAL_BANKROLL:.2f} | {LEVERAGE}x leverage")

        # ============================================================
        # 5. RESET Vault Cycle (Firestore)
        # ============================================================
        print("\n🏦 5/8 Resetando vault_management/current_cycle...")
        vault_cycle_data = {
            "cycle_number": 1,
            "mega_cycle_number": 1,
            "mega_cycle_wins": 0,
            "mega_cycle_total": 0,
            "mega_cycle_profit": 0.0,
            "cycle_start_bankroll": REAL_BANKROLL,
            "cycle_bankroll": REAL_BANKROLL,
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
            "next_entry_value": REAL_BANKROLL * 0.10,
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        firestore_db.collection("vault_management").document("current_cycle").set(vault_cycle_data)
        print(f"   ✅ Vault Cycle #1 iniciado com ${REAL_BANKROLL:.2f}")

        # ============================================================
        # 6. CLEAR RTDB Nodes
        # ============================================================
        print("\n🛰️ 6/8 Limpando nodes RTDB...")
        nodes_to_clear = ["radar_pulse", "live_slots", "market_radar", "system_state", "vault_status", "chat_status"]
        for node in nodes_to_clear:
            try:
                rtdb.child(node).delete()
            except:
                pass
        print("   ✅ RTDB nodes limpos: " + ", ".join(nodes_to_clear))

        # ============================================================
        # 7. RE-INITIALIZE RTDB Live Slots
        # ============================================================
        print("\n🎰 7/8 Inicializando live_slots no RTDB...")
        rtdb_slots = {str(i): reset_slot for i in range(1, 5)}
        rtdb.child("live_slots").set(rtdb_slots)
        print("   ✅ live_slots 1-4 inicializados no RTDB.")

        # ============================================================
        # 8. RE-INITIALIZE RTDB Vault Status
        # ============================================================
        print("\n🏦 8/8 Inicializando vault_status no RTDB...")
        rtdb.child("vault_status").set({
            "cycle_number": 1,
            "mega_cycle_number": 1,
            "mega_cycle_wins": 0,
            "cycle_start_bankroll": REAL_BANKROLL,
            "cycle_profit": 0.0,
            "total_trades_cycle": 0,
            "sniper_wins": 0,
            "used_symbols_in_cycle": [],
            "sniper_mode_active": True,
            "in_admiral_rest": False
        })
        print(f"   ✅ vault_status inicializado com ${REAL_BANKROLL:.2f}")

        # ============================================================
        # DONE
        # ============================================================
        print("\n" + "=" * 60)
        print("🔴 GO REAL RESET COMPLETO!")
        print("=" * 60)
        print(f"💰 Banca: ${REAL_BANKROLL:.2f}")
        print(f"📊 Margem por trade: ${REAL_BANKROLL * 0.10:.2f} (10%)")
        print(f"⚡ Leverage: {LEVERAGE}x")
        print(f"🎯 Alvo: 2% preço = 100% ROI")
        print(f"🎰 Slots: 4 disponíveis")
        print(f"🏦 Ciclo: #1 (0/10 wins)")
        print("=" * 60)
        print("⚠️  Inicie o backend com: python run_backend.py")
        print("⚠️  Verifique no health check: http://localhost:8085/health")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    go_real_reset()
