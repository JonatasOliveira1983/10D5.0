import asyncio
import logging
from services.signal_generator import signal_generator
from services.bybit_rest import bybit_rest_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyV7")

async def main():
    symbol = "BTCUSDT.P"
    logger.info(f"--- VERIFYING V7.0 PRECISION FOR {symbol} ---")
    
    # 1. Test Fibonacci
    logger.info("Testing Fibonacci Levels...")
    fib = await signal_generator.get_fibonacci_levels(symbol, interval="60")
    if fib:
        logger.info(f"✅ Fibonacci Calculated. Direction: {fib['direction']}")
        logger.info(f"Golden Zone: {fib['golden_zone']}")
    else:
        logger.error("❌ Fibonacci Calculation Failed.")

    # 2. Test Orderbook Walls
    logger.info("Testing Orderbook Walls...")
    walls = await signal_generator.get_orderbook_walls(symbol)
    if walls:
        logger.info(f"✅ Walls Detected. Buy Walls: {walls['buy_walls']} | OBI: {walls['obi']}")
    else:
        logger.error("❌ Wall Detection Failed.")

    # 3. Test Entry Triggers Confluence
    logger.info("Testing Entry Trigger Confluences...")
    trigger = await signal_generator.get_5m_entry_triggers(symbol, "Buy", zones_15m={})
    logger.info(f"✅ Trigger Info: Confidence={trigger['confidence']:.1f}% | Type={trigger['trigger_type']}")

    logger.info("--- V7.0 VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
