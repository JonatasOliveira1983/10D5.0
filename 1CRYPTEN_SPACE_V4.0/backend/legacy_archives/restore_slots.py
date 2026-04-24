import asyncio
from services.bybit_rest import bybit_rest_service
from services.sovereign_service import sovereign_service
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def run():
    await sovereign_service.initialize()
    await bybit_rest_service.initialize()
    
    if not sovereign_service.db:
        print("Erro db")
        return
        
    # Get prices individually to avoid list parsing issues
    try:
        ltc_resp = await asyncio.to_thread(bybit_rest_service.session.get_tickers, category="linear", symbol="LTCUSDT")
        ltc_price = float(ltc_resp['result']['list'][0]['lastPrice'])
        
        bnb_resp = await asyncio.to_thread(bybit_rest_service.session.get_tickers, category="linear", symbol="BNBUSDT")
        bnb_price = float(bnb_resp['result']['list'][0]['lastPrice'])
    except Exception as e:
        print(f"Error fetching prices: {e}")
        ltc_price = 50.0  # Safe fallbacks if API fails
        bnb_price = 610.0
    
    print(f"Current Prices - LTC: {ltc_price} | BNB: {bnb_price}")
    
    # LTC Original: Sell 53.07 (Today at 06:20 UTC)
    # BNB Original: Sell 618.80 (Today at 08:09 UTC)
    
    ltc_data = {
        "id": 1,
        "symbol": "LTCUSDT",
        "side": "Sell",
        "entry_price": 53.07,
        "qty": 9.4,
        "current_stop": 54.13, # ~2% SL from entry 53.07
        "target_price": 50.0,
        "status_risco": "ATIVO",
        "pnl_percent": ((53.07 - ltc_price) / 53.07) * 100 * 50,
        "opened_at": 1772950821,
        "pensamento": "V33.0 [RESTORED] Original Slot 1 order overwritten by BNB bug. Logic V34.2 fix applied.",
        "leverage": 50,
        "slot_type": "SWING",
        "entry_margin": 9.98
    }
    
    bnb_data = {
        "id": 2,
        "symbol": "BNBUSDT",
        "side": "Sell",
        "entry_price": 618.8,
        "qty": 0.81,
        "current_stop": 623.74,
        "target_price": 600.23,
        "status_risco": "ATIVO",
        "pnl_percent": ((618.8 - bnb_price) / 618.8) * 100 * 50,
        "opened_at": 1772957386,
        "pensamento": "V33.0 [RELOCATED] New order initially overwritten Slot 1. Relocated to Slot 2.",
        "leverage": 50,
        "slot_type": "SWING",
        "entry_margin": 10.02
    }
    
    await sovereign_service.update_slot(1, ltc_data)
    await sovereign_service.update_slot(2, bnb_data)
    
    print("Slots 1 (LTC) and 2 (BNB) successfully restored/relocated.")

if __name__ == "__main__":
    asyncio.run(run())
