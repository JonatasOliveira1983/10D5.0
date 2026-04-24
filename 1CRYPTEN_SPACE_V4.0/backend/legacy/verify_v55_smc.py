import asyncio
import logging
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.bybit_ws import bybit_ws_service
from services.signal_generator import signal_generator
from services.agents.macro_analyst import macro_analyst
from services.bybit_rest import bybit_rest_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyV55")

async def test_v55_components():
    logger.info("🚀 Starting V55.0 Verification...")

    # 1. Test FVG Detection
    symbol = "BTCUSDT"
    logger.info(f"🔍 Testing FVG Detection for {symbol}...")
    fvgs = await signal_generator.detect_fvg(symbol, interval="15")
    if fvgs:
        logger.info(f"✅ Found {len(fvgs)} FVGs: {fvgs[:2]}")
    else:
        logger.info("ℹ️ No active FVGs found at the moment (market efficiency!).")

    # 2. Test Market Structure (CHoCH/BoS)
    logger.info(f"🔍 Testing Market Structure for {symbol}...")
    structure = await signal_generator.detect_choch_and_bos(symbol)
    logger.info(f"✅ Structure Status: {structure.get('status')} | Swing High: {structure.get('swing_high')}")

    # 3. Test BTC Dominance & Macro Bias
    logger.info("🔍 Testing BTC Dominance & Macro Bias...")
    macro_data = await macro_analyst._get_macro_bias()
    logger.info(f"✅ Macro Bias: {macro_data}")
    
    # 4. Check WebSocket Metrics (Simulated since WS needs a running loop)
    logger.info("🔍 Checking OBI/VAMP Cache state...")
    # Mock data to verify the logic flow if needed, or just check if initialized
    logger.info(f"✅ OBI Cache keys: {list(bybit_ws_service.obi_cache.keys())}")
    logger.info(f"✅ VAMP Cache keys: {list(bybit_ws_service.vamp_cache.keys())}")

    logger.info("🏁 Verification Complete!")

if __name__ == "__main__":
    asyncio.run(test_v55_components())
