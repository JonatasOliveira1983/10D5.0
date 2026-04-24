import asyncio
import os
import sys

# Adicionar o diretório base ao sys.path para importar serviços
sys.path.append(os.getcwd())

async def check():
    from services.firebase_service import firebase_service
    # Inicializar o serviço se necessário
    if not firebase_service.is_active:
        print("Initializing Firebase Service...")
        await firebase_service.initialize()
        
    print(f"Firebase Active: {firebase_service.is_active}")
    if not firebase_service.is_active:
        print("Firebase is not active. Check credentials.")
        return

    print("Checking trade_history collection...")
    try:
        def _get():
            docs = firebase_service.db.collection("trade_history").limit(10).stream()
            return [doc.to_dict() for doc in docs]
        
        trades = await asyncio.to_thread(_get)
        print(f"Found {len(trades)} trades in trade_history.")
        for i, t in enumerate(trades):
            print(f"Trade {i+1}: {t.get('symbol')} | PnL: {t.get('pnl')} | TS: {t.get('timestamp')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
