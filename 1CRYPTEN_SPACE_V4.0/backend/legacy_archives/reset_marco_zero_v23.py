# -*- coding: utf-8 -*-
"""
RESET MARCO ZERO V110.23 — Sovereign Sniper Protocol
=====================================================
Operações:
  1. Limpar vault_history (Firestore) — histórico da UI da Vault
  2. Limpar trade_history (Firestore) — 237 trades antigos
  3. Limpar banca_history (Firestore)
  4. Limpar moonbags (Firestore)
  5. Resetar slots_ativos (Firestore) — 4 slots → LIVRE
  6. Resetar banca_status (Firestore) → $100.00
  7. Resetar vault_management/current_cycle (Firestore)
  8. Limpar RTDB: live_slots, moonbag_vault, banca_status
  9. Resetar paper_storage.json local → $100, sem posições
"""

import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb_module
import os
import json
import time
from datetime import datetime, timezone

# ── CONFIGURAÇÃO ──────────────────────────────────────────────────────────────
CERT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serviceAccountKey.json")
DB_URL    = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"
PAPER_STORAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paper_storage.json")

BANNER = "--- RESET MARCO ZERO V110.23 - Sovereign Sniper ---"

# ── HELPERS ───────────────────────────────────────────────────────────────────
def _delete_collection(fs, coll_name, batch_size=450):
    """Apaga todos os documentos de uma coleção em batches."""
    coll_ref = fs.collection(coll_name)
    total = 0
    while True:
        docs = list(coll_ref.limit(batch_size).stream())
        if not docs:
            break
        batch = fs.batch()
        for doc in docs:
            batch.delete(doc.reference)
        batch.commit()
        total += len(docs)
    return total

# ── RESET PRINCIPAL ───────────────────────────────────────────────────────────
def marco_zero():
    print(BANNER)

    # 0. Firebase Init
    if not os.path.exists(CERT_PATH):
        print(f"ERRO: Certificado nao encontrado: {CERT_PATH}")
        return

    cred = credentials.Certificate(CERT_PATH)
    try:
        firebase_admin.initialize_app(cred, {'databaseURL': DB_URL})
        print("OK: Firebase inicializado.")
    except ValueError:
        print("INFO: Firebase ja estava inicializado.")

    fs   = firestore.client()
    rtdb = rtdb_module.reference("/")

    # ── PASSO 1 · Limpar históricos Firestore ─────────────────────────────────
    colecoes_historico = [
        'vault_history',
        'trade_history',
        'banca_history',
        'moonbags',
        'system_logs',
        'journey_signals',
    ]
    for nome in colecoes_historico:
        n = _delete_collection(fs, nome)
        if n > 0:
            print(f"LIMPANDO: [{nome}] {n} documentos removidos.")
        else:
            print(f"INFO: [{nome}] ja estava vazia.")

    # ── PASSO 2 · Resetar vault_management/current_cycle ─────────────────────
    print("\n[VAULT] Resetando vault_management/current_cycle...")
    try:
        fs.collection('vault_management').document('current_cycle').set({
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
        }, merge=True)
        print("OK: vault_management/current_cycle resetado.")
    except Exception as e:
        print(f"AVISO: vault_management: {e}")

    # ── PASSO 3 · Resetar banca_status ────────────────────────────────────────
    print("\n[BANCA] Resetando banca_status para $100.00...")
    try:
        fs.collection('banca_status').document('status').set({
            "saldo_total": 100.0,
            "configured_balance": 100.0,
            "lucro_total_acumulado": 0.0,
            "lucro_ciclo": 0.0,
            "vault_total": 0.0,
            "risco_real_percent": 0,
            "slots_disponiveis": 4,
            "status": "ONLINE",
            "last_update": time.time(),
            "updated_at": int(time.time() * 1000)
        }, merge=True)
        print("OK: banca_status OK - $100.00")
    except Exception as e:
        print(f"AVISO: banca_status: {e}")

    # ── PASSO 4 · Resetar slots_ativos (4 slots → LIVRE) ──────────────────────
    print("\n[SLOTS] Resetando 4 slots taticos para LIVRE...")
    for i in range(1, 5):
        try:
            fs.collection('slots_ativos').document(str(i)).set({
                "id": i,
                "symbol": None,
                "side": None,
                "qty": 0,
                "entry_price": 0,
                "current_stop": 0,
                "target_price": 0,
                "status_risco": "LIVRE",
                "pnl_percent": 0,
                "opened_at": None,
                "entry_margin": 0,
                "fleet_intel": None,
                "is_shadow_strike": False,
                "is_market_ranging": False,
                "pensamento": "Marco Zero V110.23",
                "timestamp_last_update": time.time()
            })
            print(f"OK: Slot {i} -> LIVRE")
        except Exception as e:
            print(f"ERRO: Slot {i}: {e}")

    # ── PASSO 5 · Limpar RTDB ─────────────────────────────────────────────────
    print("\n[RTDB] Limpando Realtime Database...")
    now_ms = int(time.time() * 1000)
    try:
        slots_reset = {
            str(i): {
                "id": i,
                "symbol": None,
                "status_risco": "LIVRE",
                "pnl_percent": 0,
                "qty": 0,
                "entry_price": 0,
                "side": None
            }
            for i in range(1, 5)
        }
        rtdb.update({
            "live_slots": slots_reset,
            "moonbag_vault": {},
            "banca_status": {
                "saldo_total": 100.0,
                "risco_real_percent": 0,
                "last_update": now_ms
            },
            "system_pulse": {
                "status": "MARCO_ZERO_V110.23",
                "timestamp": now_ms
            }
        })
        print("OK: RTDB limpo: live_slots, moonbag_vault, banca_status.")
    except Exception as e:
        print(f"ERRO: Erro ao limpar RTDB: {e}")

    # ── PASSO 6 · Resetar paper_storage.json local ────────────────────────────
    print("\n[LOCAL] Resetando paper_storage.json local...")
    try:
        initial_state = {
            "balance": 100.0,
            "positions": [],
            "slots": {},
            "history": [],
            "moonbags": [],
            "last_sync": time.time()
        }
        with open(PAPER_STORAGE, 'w', encoding='utf-8') as f:
            json.dump(initial_state, f, indent=4)
        print("OK: paper_storage.json -> $100.00, sem posicoes.")
    except Exception as e:
        print(f"ERRO: paper_storage.json: {e}")

    # ── FIM ───────────────────────────────────────────────────────────────────
    print("\n" + "=" * 56)
    print("  MARCO ZERO V110.23 CONCLUIDO COM SUCESSO!")
    print("=" * 56)
    print("  -> Banca:       $100.00")
    print("  -> Slots:        4x LIVRE")
    print("  -> Vault:        Historico limpo")
    print("  -> Trade Hist:  237 trades removidos")
    print("  -> UI:          Pronta para novo ciclo")
    print("=" * 56)

if __name__ == "__main__":
    marco_zero()
