import asyncio
import json
from services.sovereign_service import sovereign_service
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def run():
    await sovereign_service.initialize()
    if not sovereign_service.db:
        print("Erro db")
        return
    
    signals_ref = sovereign_service.db.collection('journey_signals')
    
    print("\n--- Fetching last 100 signals ---")
    query = signals_ref.order_by('timestamp', direction='DESCENDING').limit(100)
    docs = await asyncio.to_thread(lambda: list(query.stream()))
    
    print(f"Found {len(docs)} signals total.")
    
    ltc_signals = []
    bnb_signals = []
    
    for doc in docs:
        d = doc.to_dict()
        sym = d.get('symbol', '').upper()
        if 'LTCUSDT' in sym:
            ltc_signals.append((doc.id, d))
        if 'BNBUSDT' in sym:
            bnb_signals.append((doc.id, d))
            
    with open("signals_detail.txt", "w", encoding="utf-8") as f:
        f.write("--- Recent LTCUSDT Signals ---\n")
        for s_id, d in ltc_signals[:10]:
            f.write(f"ID: {s_id} | Outcome: {d.get('outcome')} | Data: {json.dumps(d, indent=2, ensure_ascii=False)}\n\n")

        f.write("\n--- Recent BNBUSDT Signals ---\n")
        for s_id, d in bnb_signals[:10]:
            f.write(f"ID: {s_id} | Outcome: {d.get('outcome')} | Data: {json.dumps(d, indent=2, ensure_ascii=False)}\n\n")

    print("Resultados salvos em signals_detail.txt")

if __name__ == "__main__":
    asyncio.run(run())
