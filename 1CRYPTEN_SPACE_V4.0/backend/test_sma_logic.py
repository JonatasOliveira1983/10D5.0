import asyncio
from services.signal_generator import signal_generator

async def test_sma_shield():
    print("starting test...")
    symbol = "BTCUSDT"
    res = await signal_generator.get_2h_macro_analysis(symbol)
    print(res)
    
if __name__ == "__main__":
    asyncio.run(test_sma_shield())
