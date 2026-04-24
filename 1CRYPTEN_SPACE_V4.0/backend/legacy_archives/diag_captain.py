import asyncio
from typing import Dict, Any
from services.sovereign_service import sovereign_service
from services.bankroll import bankroll_manager
from config import settings

async def diagnostic_unopened_orders():
    print("--- Inicializando Conexão Firebase ---")
    await sovereign_service.initialize()
    if not sovereign_service.db:
        print("FALHA: Não foi possível conectar ao Firestore.")
        return

    print("--- Diagnóstico: Sinais Gerados vs Ordens Não Abertas ---")
    
    # 1. Obter os slots atuais
    try:
        slots = await sovereign_service.get_active_slots()
        occupied = 0
        for slot in slots:
            if slot.get("symbol"):
                occupied += 1
                print(f"Slot {slot['id']}: OCUPADO ({slot['symbol']} - {slot['side']})")
            else:
                print(f"Slot {slot['id']}: LIVRE")
        print(f"\nSlots ocupados: {occupied}/4")
    except Exception as e:
        print(f"Erro ao obter slots: {e}")
    
    # 2. Obter lock atômico do bankroll
    pending = bankroll_manager.pending_slots
    if pending:
        print(f"\n[ATENÇÃO] Existem locks atômicos pendentes: {pending}")
    else:
        print("\nNenhum lock atômico travando o sistema.")
    
    # 3. Obter os últimos eventos no Firestore
    print("\n--- Últimos 10 Sinais Avaliados pelo Capitão (Eventos) ---")
    try:
        events_ref = sovereign_service.db.collection('10D_logs')
        query = events_ref.where('category', '==', 'SNIPER').order_by('timestamp', direction='DESCENDING').limit(20)
        docs = await asyncio.to_thread(query.stream)
        
        count = 0
        for doc in docs:
            data = doc.to_dict()
            msg = data.get('message', '')
            if "rejected:" in msg or "ignored:" in msg or "blocked:" in msg or "dropped:" in msg or "SELECTS BEST SIGNAL" in msg or "SNIPER SHOT DEPLOYED" in msg or "MOMENTUM" in msg or "Bloqueado" in msg:
                 print(f"{data.get('timestamp')}: {msg}")
                 count += 1
                 if count >= 10: break
    except Exception as e:
         print(f"Erro ao buscar eventos: {e}")

    print("\n--- Últimos 5 Sinais Gerados pelo Signal Generator ---")
    try:
        signals_ref = sovereign_service.db.collection('10D_signals')
        query_sig = signals_ref.order_by('timestamp', direction='DESCENDING').limit(5)
        docs_sig = await asyncio.to_thread(query_sig.stream)
        
        for doc in docs_sig:
            data = doc.to_dict()
            print(f"{data.get('timestamp')}: {data.get('symbol')} ({data.get('side')}) - Score {data.get('score')} - Layer: {data.get('layer', 'MOMENTUM')} - Status: {data.get('outcome', 'N/A')}")
    except Exception as e:
         print(f"Erro ao buscar sinais: {e}")

if __name__ == "__main__":
    asyncio.run(diagnostic_unopened_orders())
