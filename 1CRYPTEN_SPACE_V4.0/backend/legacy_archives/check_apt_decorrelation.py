import asyncio
import os
import sys

# Force UTF-8
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.signal_generator import signal_generator
from services.bybit_ws import bybit_ws_service

async def check_live():
    print("Checking live decorrelation for APTUSDT...")
    # Wait a bit for WS to have some data (though it should be running in the background)
    # But since we are a separate process, we need to wait for it to connect if we start it here.
    # Actually, we can just use the signal_generator which will try to fetch whatever is available.
    
    # We might need to initialize some things if they are not running.
    # But usually, these services are singletons that start on first call or need manual start.
    
    try:
        # Let's try to get the real status
        result = await signal_generator.detect_btc_decorrelation("APTUSDT")
        
        print("\n--- RESULTADO DA DESCORRELAÇÃO (APTUSDT) ---")
        print(f"Status: {'✅ DESCORRELACIONADA' if result.get('is_decorrelated') else '❌ CORRELACIONADA'}")
        print(f"Confiança: {result.get('confidence')}%")
        print(f"Direção Sugerida: {result.get('direction')}")
        print(f"Sinais Detectados: {result.get('signals')}")
        print(f"Motivo: {result.get('reason')}")
        
        if result.get('is_decorrelated'):
            print("\n🕒 TEMPO NO GUARDIÃO: 30 MINUTOS (Modo Especial)")
        else:
            print("\n🕒 TEMPO NO GUARDIÃO: 10 MINUTOS (Modo Zumbi Padrão)")
            
    except Exception as e:
        print(f"Erro ao verificar: {e}")

if __name__ == "__main__":
    asyncio.run(check_live())
