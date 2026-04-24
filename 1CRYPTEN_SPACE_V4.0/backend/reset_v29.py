# -*- coding: utf-8 -*-
"""
V29.0 Full Reset V2: Direct Firestore overwrite (no merge) + RTDB live_slots cleanup.
"""
import asyncio
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ["PYTHONIOENCODING"] = "utf-8"

from services.firebase_service import firebase_service

async def full_reset():
    print("=" * 60)
    print("[RESET] V29.0 FULL SYSTEM RESET V2 (Direct Overwrite)")
    print("=" * 60)
    
    await firebase_service.initialize()
    db = firebase_service.db
    rtdb = firebase_service.rtdb
    
    if not db:
        print("ERRO: Sem conexao ao Firestore!")
        return
    
    # 1. FORCE-OVERWRITE Slots 1-4 in Firestore (NO MERGE)
    print("\n[1/6] Resetando Slots 1-4 (Firestore overwrite)...")
    empty_slot = {
        "id": 0,
        "symbol": "",
        "entry_price": 0,
        "current_stop": 0,
        "entry_margin": 0,
        "status_risco": "IDLE",
        "side": "",
        "pnl_percent": 0,
        "target_price": 0,
        "qty": 0,
        "slot_type": "",
        "pattern": "",
        "pensamento": "",
        "structural_target": 0,
        "target_extended": 0,
        "move_room_pct": 0,
        "liq_price": 0,
        "leverage": 50,
        "opened_at": 0,
        "timestamp_last_update": 0
    }
    for i in range(1, 5):
        doc = empty_slot.copy()
        doc["id"] = i
        # Use .set() WITHOUT merge to completely overwrite the document
        db.collection("slots_ativos").document(str(i)).set(doc)
        print(f"   OK: Slot {i} -> IDLE (Firestore overwritten)")
    
    # 2. Clear RTDB live_slots
    print("\n[2/6] Limpando RTDB live_slots...")
    if rtdb:
        try:
            rtdb_empty = {}
            for i in range(1, 5):
                rtdb_empty[str(i)] = {
                    "id": i,
                    "symbol": "",
                    "entry_price": 0,
                    "current_stop": 0,
                    "status_risco": "IDLE",
                    "side": "",
                    "pnl_percent": 0,
                    "slot_type": "",
                    "qty": 0,
                    "target_price": 0
                }
            rtdb.child("live_slots").set(rtdb_empty)
            print("   OK: RTDB live_slots limpo")
        except Exception as e:
            print(f"   AVISO: Erro ao limpar RTDB: {e}")
    
    # 3. Limpar trade_history
    print("\n[3/6] Limpando trade_history...")
    trades = db.collection("trade_history").stream()
    count = 0
    for doc in trades:
        doc.reference.delete()
        count += 1
    print(f"   OK: {count} trades removidos")
    
    # 4. Limpar banca_history
    print("\n[4/6] Limpando banca_history...")
    banca = db.collection("banca_history").stream()
    count = 0
    for doc in banca:
        doc.reference.delete()
        count += 1
    print(f"   OK: {count} snapshots removidos")
    
    # 5. Resetar bankroll para $100
    print("\n[5/6] Resetando bankroll para $100...")
    banca_data = {
        "id": "status",
        "configured_balance": 100.0,
        "saldo_total": 100.0,
        "saldo_real_bybit": 0,
        "lucro_total_acumulado": 0,
        "lucro_ciclo": 0,
        "risco_real_percent": 0,
        "slots_disponiveis": 4,
        "leverage": 50
    }
    db.collection("banca_status").document("status").set(banca_data)
    if rtdb:
        rtdb.child("banca_status").set(banca_data)
    print("   OK: Bankroll -> $100.00")
    
    # 6. Limpar paper_storage.json
    print("\n[6/6] Limpando paper_storage.json...")
    paper_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paper_storage.json")
    clean_paper = {
        "balance": 100.0,
        "positions": [],
        "pending_closures": [],
        "recently_closed": {}
    }
    with open(paper_file, 'w') as f:
        json.dump(clean_paper, f, indent=2)
    print("   OK: Paper positions zeradas, balance -> $100.00")
    
    # Bonus: Limpar cooldowns
    print("\n[BONUS] Limpando cooldowns...")
    try:
        cooldowns = db.collection("sl_cooldowns").stream()
        count = 0
        for doc in cooldowns:
            doc.reference.delete()
            count += 1
        print(f"   OK: {count} cooldowns removidos")
    except:
        print("   Skip: Sem cooldowns")
    
    # Bonus 2: Limpar vault cycle
    print("[BONUS] Resetando vault cycle...")
    try:
        db.collection("vault").document("cycle_status").set({
            "cycle_number": 1,
            "cycle_start_bankroll": 100.0,
            "cycle_profit": 0,
            "sniper_wins": 0,
            "sniper_losses": 0,
            "sniper_total": 0,
            "vault_total": 0,
            "is_cycle_active": True
        })
        print("   OK: Vault cycle resetado")
    except:
        print("   Skip: Erro ao resetar vault")
    
    print("\n" + "=" * 60)
    print("RESET V2 COMPLETO! Sistema 100%% limpo para V30.0 Anti-Fake-Move.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(full_reset())
