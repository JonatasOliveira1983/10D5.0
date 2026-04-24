from services.sovereign_service import sovereign_service
import asyncio
import json
import time

async def test_serialization():
    market_context = {
        "btc_direction": "UP",
        "btc_strength": 80,
        "btc_regime": "TRENDING",
        "btc_adx": 30
    }
    
    signals = []
    decisions = []
    
    data = sovereign_service._clean_mojibake(sovereign_service._make_json_safe({
        "signals": signals,
        "decisions": decisions,
        "market_context": market_context,
        "updated_at": int(time.time() * 1000)
    }))
    
    print("--- Serialized Data Keys ---")
    print(data.keys())
    print("--- market_context content ---")
    print(json.dumps(data.get("market_context"), indent=2))

if __name__ == "__main__":
    asyncio.run(test_serialization())
