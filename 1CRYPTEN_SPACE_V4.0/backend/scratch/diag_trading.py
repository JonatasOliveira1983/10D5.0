import asyncio
import os
import sys

# Corrige o path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

async def diag():
    print("--- DIAGNÓSTICO DO CAPITÃO E ORÁCULO ---")
    try:
        from services.agents.oracle_agent import oracle_agent
        from services.signal_generator import signal_generator
        from services.bybit_ws import bybit_ws_service
        from services.bybit_rest import bybit_rest_service
        from config import settings
        
        # Initialize necessary services (mocking firebase if needed or just skipping)
        await bybit_rest_service.initialize()
        
        print("\n1. Verificando Oracle Agent Context:")
        ctx = oracle_agent.get_validated_context()
        print(f"Status: {ctx.get('status')}")
        print(f"BTC ADX: {ctx.get('btc_adx')}")
        print(f"BTC Direction: {ctx.get('btc_direction')}")
        print(f"Remaining Wait: {ctx.get('remaining_wait')}s")
        
        print("\n2. Verificando BybitWS Metrics:")
        print(f"WS BTC ADX: {bybit_ws_service.btc_adx}")
        print(f"WS BTC Var 1h: {bybit_ws_service.btc_variation_1h}%")
        print(f"WS BTC Var 15m: {bybit_ws_service.btc_variation_15m}%")
        
        print("\n3. Calculando ADX via SignalGenerator:")
        regime = await signal_generator.detect_market_regime("BTCUSDT.P")
        print(f"SigGen ADX: {regime.get('adx')}")
        print(f"SigGen Regime: {regime.get('regime')}")
        
    except Exception as e:
        print(f"Erro no diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diag())
