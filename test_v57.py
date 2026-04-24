import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))

from services.signal_generator import signal_generator
from services.bybit_ws import bybit_ws_service

async def run_test():
    print("🚀 Running V57.0 Isolated Decorrelation Test...")
    
    # Mock services
    from services.bybit_rest import bybit_rest_service
    
    # Mock methods
    bybit_ws_service.get_current_price = lambda s: 1.5
    bybit_ws_service.get_cvd_score = lambda s: 50000
    
    async def mock_klines(symbol="", interval="", limit=2):
        return [[0, "1.50", "1.51", "1.48", "1.50", 0], [0, "1.48", "1.49", "1.47", "1.488", 0]]
    bybit_rest_service.get_klines = mock_klines
    
    # 🧪 Test 1: BTC Lateral (0.1%)
    bybit_ws_service.btc_variation_1h = 0.1
    res1 = await signal_generator.detect_btc_decorrelation("XRPUSDT", alt_cvd=80000, alt_ls_ratio=1.8, alt_oi=50000)
    print(f"Test 1 (Lateral): Res={res1['is_decorrelated']} Reason={res1['reason']} Confidence={res1['confidence']}")
    
    # 🧪 Test 2: BTC Moving (1.5%)
    bybit_ws_service.btc_variation_1h = 1.5
    res2 = await signal_generator.detect_btc_decorrelation("XRPUSDT", alt_cvd=80000, alt_ls_ratio=1.8, alt_oi=50000)
    print(f"Test 2 (Moving): Res={res2['is_decorrelated']} Reason={res2['reason']} Confidence={res2['confidence']}")
    
    if res2['reason'] == 'btc_not_lateral':
        print("✅ Correct: Test 2 detected 'btc_not_lateral'")
    else:
        print(f"❌ Error: Test 2 expected 'btc_not_lateral', got '{res2['reason']}'")

if __name__ == "__main__":
    asyncio.run(run_test())
