import asyncio
from services.firebase_service import firebase_service
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def fetch_signals():
    await firebase_service.initialize()
    if not firebase_service.db:
        print("Erro db")
        return
    
    # O firebase_service.log_signal usa doc_ref = self.db.collection('signals_log').document(signal_data["id"])
    signals_ref = firebase_service.db.collection('signals_log')
    query_sig = signals_ref.order_by('timestamp', direction='DESCENDING').limit(50)
    
    try:
        docs = await asyncio.to_thread(lambda: list(query_sig.stream()))
        
        with open("diag_out.txt", "w", encoding="utf-8") as f:
            for doc in docs:
                d = doc.to_dict()
                f.write(f"{d.get('timestamp')}: {d.get('symbol')} {d.get('side')} - Score: {d.get('score')} Layer: {d.get('layer')} Status: {d.get('outcome', 'N/A')}\n")
        print("Sinais gravados em diag_out.txt")
    except Exception as e:
        print(f"Erro no loop de query stream: {e}")

asyncio.run(fetch_signals())
