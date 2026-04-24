# -*- coding: utf-8 -*-
import asyncio
from services.agents.quartermaster import quartermaster_agent

async def test_quartermaster():
    print("Testing Quartermaster V110.135...")
    
    # 1. Smooth Bar (Low Wicks)
    # Open 10, Close 12, High 12.2, Low 9.8
    # Body = 2, Range = 2.4. Wick = (2.4 - 2) / 2 = 0.2
    wick_smooth = quartermaster_agent.calculate_wick_intensity(12.2, 9.8, 10, 12)
    print(f"Smooth Wick Intensity: {wick_smooth:.2f}")
    
    # 2. Extreme Bar (High Wicks)
    # Open 10, Close 10.5, High 15, Low 5
    # Body = 0.5, Range = 10. Wick = (10 - 0.5) / 0.5 = 19
    wick_extreme = quartermaster_agent.calculate_wick_intensity(15, 5, 10, 10.5)
    print(f"Extreme Wick Intensity: {wick_extreme:.2f}")
    
    # 3. Armory Check - Smooth
    armory_smooth = await quartermaster_agent.check_armory("BTCUSDT", {"wick_intensity": 0.2}, {"btc_adx": 30})
    print(f"Smooth Armory: {armory_smooth['leverage']}x, Multiplier={armory_smooth['margin_multiplier']}x")
    
    # 4. Armory Check - Jumpy
    armory_jumpy = await quartermaster_agent.check_armory("SOLUSDT", {"wick_intensity": 0.5}, {"btc_adx": 30})
    print(f"Jumpy Armory: {armory_jumpy['leverage']}x, Multiplier={armory_jumpy['margin_multiplier']}x")
    
    # 5. Armory Check - Extreme (Blocked by ADX)
    armory_block = await quartermaster_agent.check_armory("DOGEUSDT", {"wick_intensity": 0.8}, {"btc_adx": 20})
    print(f"Extreme Block Check: Block Reason = {armory_block['block_reason']}")
    
    # 6. Armory Check - Extreme (Allowed by high ADX)
    armory_extreme = await quartermaster_agent.check_armory("DOGEUSDT", {"wick_intensity": 0.8}, {"btc_adx": 35})
    print(f"Extreme Allowed Check: Leverage = {armory_extreme['leverage']}x")

if __name__ == "__main__":
    asyncio.run(test_quartermaster())
