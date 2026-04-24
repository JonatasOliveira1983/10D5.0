import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.sovereign_service import sovereign_service
from services.bankroll import bankroll_manager
from services.bybit_rest import bybit_rest_service

async def test_bankroll():
    print("Iniciando teste de Bankroll V33.1 (Atr Fix)...")
    await sovereign_service.initialize()
    await bybit_rest_service.initialize(paper_mode=True)
    
    mock_signal = {
        "id": "teste-mock-direct",
        "symbol": "BTCUSDT",
        "score": 99,
        "side": "Buy",
        "layer": "SNIPER",
        "expected_roi": 150.0,
        "strategy_type": "SWING",
        "indicators": {
            "atr": "not_a_float", # Forcing the try/except to trigger
            "pattern": "MOCK_FIX_TEST",
            "move_room_pct": 2.5
        }
    }

    try:
        # Tenta abrir com slot 3 mockado
        print("Enviando sinal para open_position...")
        result = await bankroll_manager.open_position("BTCUSDT", "Buy", 3, "SWING", 99, mock_signal)
        print(f"Resultado real de Execução: {result}")
    except Exception as e:
        print(f"CRASH FATAL: {e}")

if __name__ == "__main__":
    asyncio.run(test_bankroll())
