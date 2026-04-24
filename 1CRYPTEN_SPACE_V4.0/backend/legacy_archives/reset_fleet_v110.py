import asyncio
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, db

# Setup Firebase
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://bybity-real-default-rtdb.firebaseio.com/'
        })
except Exception as e:
    print(f"Firebase Init Error: {e}")

fs = firestore.client()
rtdb = db.reference()

async def reset_fleet():
    print("🚀 [RESET] Iniciando Limpeza Total V110.19.3...")

    # 1. Reset Banca (Firestore)
    try:
        fs.collection('vault_status').document('current').update({
            'configured_balance': 100.0,
            'total_pnl': 0.0,
            'cycle_start_bankroll': 100.0,
            'last_reset': firestore.SERVER_TIMESTAMP
        })
        print("✅ Banca resetada para $100.00")
    except:
        print("⚠️ Erro ao resetar banca no Firestore.")

    # 2. Limpar Histórico de Trades
    try:
        trades = fs.collection('vault_history').stream()
        batch = fs.batch()
        count = 0
        for t in trades:
            batch.delete(t.reference)
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = fs.batch()
        batch.commit()
        print(f"✅ Histórico de trades limpo ({count} registros).")
    except Exception as e:
        print(f"⚠️ Erro ao limpar histórico: {e}")

    # 3. Limpar RTDB (Slots + Eventos)
    try:
        # Reset Slots
        slots = {}
        for i in range(1, 5):
            slots[str(i)] = {
                "id": i,
                "symbol": None,
                "status_risco": "LIVRE",
                "pnl_percent": 0.0,
                "side": None,
                "entry_price": 0,
                "current_stop": 0,
                "target_price": 0,
                "qty": 0,
                "slot_type": "SNIPER"
            }
        rtdb.child('slots').set(slots)
        
        # Limpar Eventos
        rtdb.child('events').delete()
        print("✅ Slots e Eventos RTDB limpos.")
    except Exception as e:
        print(f"⚠️ Erro ao limpar RTDB: {e}")

    # 4. Limpar Paper Storage Local
    try:
        if os.path.exists('paper_storage.json'):
            empty_state = {
                "positions": [],
                "moonbags": [],
                "balance": 100.0,
                "history": []
            }
            with open('paper_storage.json', 'w') as f:
                json.dump(empty_state, f, indent=2)
            print("✅ Armazenamento Paper local limpo com estrutura correta.")
    except Exception as e:
        print(f"⚠️ Erro ao limpar paper_storage.json: {e}")

    print("\n✨ [RESET CONCLUÍDO] Frota V110 Pronta para Combate!")

if __name__ == "__main__":
    asyncio.run(reset_fleet())
