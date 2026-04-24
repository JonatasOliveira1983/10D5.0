
import asyncio
import time
from services.sovereign_service import sovereign_service

async def create_test_moonbag():
    await sovereign_service.initialize()
    test_data = {
        "symbol": "BTCUSDT",
        "side": "Buy",
        "entry_price": 50000.0,
        "qty": 0.001,
        "promoted_at": time.time(),
        "original_slot": 1,
        "strategy": "Sniper TREND"
    }
    # Usando o Admin SDK via sovereign_service interno se possível, ou direto
    try:
        doc_ref = sovereign_service.db.collection("moonbags").document("test_moonbag_1")
        doc_ref.set(test_data)
        print("✅ Moonbag de teste criada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar moonbag: {e}")

if __name__ == "__main__":
    asyncio.run(create_test_moonbag())
