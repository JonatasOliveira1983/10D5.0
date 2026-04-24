import asyncio
from services.firebase_service import FirebaseService
import json

async def fetch_linkusdt_trade():
    try:
        fb = FirebaseService()
        await fb.initialize()
        
        collections_to_check = ['vault_history_live', 'trade_history_live', 'vault_history_paper', 'trade_history_paper']
        trades = []
        for coll in collections_to_check:
            docs = fb.db.collection(coll).document('history').collection('trades') \
                .order_by('close_time', direction='DESCENDING') \
                .limit(100) \
                .stream()
            for doc in docs:
                t = doc.to_dict()
                if t.get('symbol') == 'LINKUSDT':
                    t['_collection'] = coll
                    trades.append(t)
                    if len(trades) >= 5:
                        break
            if len(trades) >= 5:
                break
            
        if not trades:
            # Tentar na paper_storage para ver se esta la? 
            # O usuario falou "historico da vault da bybit" sugerindo REAL.
            # Entao vault_history_live
            print("Nenhuma trade de LINKUSDT encontrada no vault_history_live limit(5). Tentando pegar todas e filtrar.")
            all_docs = fb.db.collection('vault_history_live').document('history').collection('trades').stream()
            for doc in all_docs:
                t = doc.to_dict()
                if t.get('symbol') == 'LINKUSDT':
                    trades.append(t)
                    
            # Order por close_time
            trades.sort(key=lambda x: x.get('close_time', ''), reverse=True)
            trades = trades[:5]

        # Serializar datetime? Firebase retorna datetime com timezone
        for t in trades:
            for k, v in t.items():
                if hasattr(v, 'isoformat'):
                    t[k] = v.isoformat()
                    
        print(json.dumps(trades, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_linkusdt_trade())
