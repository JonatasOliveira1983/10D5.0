import asyncio
import logging
import time
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.agents.onchain_whale_watcher import on_chain_whale_watcher
from services.agents.sentiment_specialist import sentiment_specialist

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyV56")

async def test_v56_onchain():
    logger.info("🚀 Starting V56.0 On-Chain Verification...")

    # 1. Mock a Whale Inflow Alert (USDT -> Bybit)
    logger.info("🧪 Injecting MOCK Whale Inflow (Potential Dump)...")
    on_chain_whale_watcher.whale_alerts = [{
        "source": "MOCK",
        "symbol": "USDT",
        "value": 15000000,
        "type": "INFLOW (Potential Dump)",
        "timestamp": time.time() - 60, # 1 minute ago
        "hash": "0xmockhash123"
    }]

    # 2. Check Sentiment for BTCUSDT
    logger.info("🔍 Testing Sentiment Specialist for BTCUSDT with Whale Inflow...")
    sentiment = await sentiment_specialist._get_sentiment("BTCUSDT")
    score_with_inflow = sentiment['data']['score']
    logger.info(f"✅ Sentiment Score with Inflow: {score_with_inflow}")

    # 3. Mock a Whale Outflow Alert (USDT -> Wallet)
    logger.info("🧪 Injecting MOCK Whale Outflow (Accumulation)...")
    on_chain_whale_watcher.whale_alerts = [{
        "source": "MOCK",
        "symbol": "ETH",
        "value": 1000,
        "type": "OUTFLOW (Accumulation)",
        "timestamp": time.time() - 60,
        "hash": "0xmockhash456"
    }]

    # 4. Check Sentiment for ETHUSDT
    logger.info("🔍 Testing Sentiment Specialist for ETHUSDT with Whale Outflow...")
    sentiment = await sentiment_specialist._get_sentiment("ETHUSDT")
    score_with_outflow = sentiment['data']['score']
    logger.info(f"✅ Sentiment Score with Outflow: {score_with_outflow}")

    logger.info("🏁 Verification Complete!")

if __name__ == "__main__":
    asyncio.run(test_v56_onchain())
