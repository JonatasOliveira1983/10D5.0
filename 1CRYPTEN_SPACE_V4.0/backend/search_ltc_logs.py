import asyncio
from services.sovereign_service import sovereign_service
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def run():
    await sovereign_service.initialize()
    if not sovereign_service.db:
        print("Erro db")
        return
    
    logs_ref = sovereign_service.db.collection('system_logs')
    
    print("\n--- Searching for LTCUSDT DEPLOYED logs (UTF-8) ---")
    query = logs_ref.order_by('timestamp', direction='DESCENDING').limit(300)
    docs = await asyncio.to_thread(lambda: list(query.stream()))
    
    with open("ltc_found_logs.txt", "w", encoding="utf-8") as f:
        for doc in docs:
            d = doc.to_dict()
            msg = d.get('message', '')
            if 'LTCUSDT' in msg or 'BNBUSDT' in msg:
                f.write(f"[{d.get('timestamp')}] {msg}\n")
            
    print("Resultados salvos em ltc_found_logs.txt")

if __name__ == "__main__":
    asyncio.run(run())
