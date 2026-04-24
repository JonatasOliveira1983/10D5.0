import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.bankroll import bankroll_manager, bybit_rest_service
from services.sovereign_service import sovereign_service

async def run_check():
    await sovereign_service.initialize()
    await bybit_rest_service.initialize()
    balance = await bankroll_manager._get_operating_balance()
    print(f"Current Operating Balance: {balance}")
    
    # Check what margin it would calculate for LTCUSDT
    info = await bybit_rest_service.get_instrument_info("LTCUSDT")
    max_lev = float(info.get("leverageFilter", {}).get("maxLeverage", 50.0))
    current_leverage = min(50.0, max_lev)
    print(f"LTCUSDT max_lev: {max_lev}, current_leverage: {current_leverage}")
    
    margin = await bankroll_manager._calculate_target_margin(balance, current_leverage)
    print(f"Calculated target margin for LTCUSDT: {margin}")
    
    # Check paper storage
    with open('paper_storage.json', 'r') as f:
        print(f"Paper Storage content: {f.read()}")

if __name__ == "__main__":
    asyncio.run(run_check())
