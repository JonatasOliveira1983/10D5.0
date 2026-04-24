import asyncio
import sys
import os
import time

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.agents.oracle_agent import OracleAgent
from services.bankroll import bankroll_manager
from services.firebase_service import firebase_service
from services.bybit_rest import bybit_rest_service

async def test_hedge_sentinel():
    print("🛡️ Iniciando Teste do Guardian Hedge (Pilar 3)...")
    
    oracle = OracleAgent()
    
    # 1. Mockar as funções de execução para evitar ordens reais mesmo no Paper durante o teste de lógica
    async def mock_open_position(symbol, side, leverage, qty, margin_usd):
        print(f"💰 [MOCK-EXECUTION] Abrindo Posição de HEDGE: {symbol} {side} Margin: ${margin_usd}")
        return {"id": "test_hedge_id", "symbol": symbol, "side": side}
    
    bybit_rest_service.open_position = mock_open_position
    
    async def mock_log_event(tag, msg, level="INFO"):
        print(f"📝 [MOCK-LOG] {level}: {msg}")
        if "GUARDIAN HEDGE ATIVADO" in msg:
            print("🎯 TESTE PASSOU: Guardian Hedge disparado com sucesso pelo Oracle!")

    firebase_service.log_event = mock_log_event

    # 2. Simular queda violenta do BTC (Crash de -3.0% em 15m)
    print("📉 Simulando Flash Crash no Oráculo (-3.0% em 15m)...")
    mock_data = {
        "btc_price": 60000,
        "btc_variation_24h": -1.0,
        "btc_variation_1h": -1.5,
        "btc_variation_15m": -3.0, # Gatilho de Pânico
        "btc_adx": 35
    }
    
    # Executa a recepção dos dados no Oráculo
    await oracle.update_market_data("BybitWS", mock_data)
    
    # Pequeno tempo para o task asssíncrono rodar
    await asyncio.sleep(2)
    
    # 3. Simular recuperação (Close Hedge)
    print("\n📈 Simulando Recuperação do Mercado (-0.4% em 15m)...")
    async def mock_close_position(symbol, side):
        print(f"💰 [MOCK-EXECUTION] Fechando Posição de HEDGE: {symbol}")
        return True
        
    bybit_rest_service.close_position = mock_close_position
    
    mock_recovery_data = {
        "btc_price": 60500,
        "btc_variation_24h": -0.8,
        "btc_variation_1h": -0.5,
        "btc_variation_15m": -0.4, # Gatilho de Estabilização
        "btc_adx": 30
    }
    
    await oracle.update_market_data("BybitWS", mock_recovery_data)
    await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_hedge_sentinel())
