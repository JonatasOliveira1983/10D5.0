import asyncio
import logging
from services.bybit_rest import bybit_rest_service
from services.bybit_ws import bybit_ws_service
from services.signal_generator import SignalGenerator

logging.basicConfig(level=logging.INFO)

async def main():
    print("Initialising REST...")
    await bybit_rest_service.initialize()
    pairs = await bybit_rest_service.get_elite_50x_pairs()
    
    # Just connect WS for our test pair
    bybit_ws_service.start(['SPXUSDT.P'])
    await asyncio.sleep(3) # let WS connect
    
    sig_gen = SignalGenerator()
    await sig_gen.get_2h_macro_analysis('SPXUSDT')
    print("2H Trend:", sig_gen.trend_cache_2h.get('SPXUSDT'))
    
    # Mock some basic WS data so Stage 1 doesn't drop it immediately
    bybit_ws_service.active_symbols = ['SPXUSDT.P']
    bybit_ws_service.turnover_24h_cache['SPXUSDT.P'] = 5000000 # 5M
    await sig_gen.calculate_rest_cvd('SPXUSDT.P')
    
    # Start the generator loop in a task, let it run for 10 seconds, then check candidates
    sig_gen.is_running = True
    task = asyncio.create_task(sig_gen.monitor_and_generate())
    await asyncio.sleep(15)
    sig_gen.is_running = False
    await task

asyncio.run(main())
