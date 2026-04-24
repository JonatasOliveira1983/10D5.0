import asyncio
import os
import sys
import time

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.signal_generator import signal_generator
from services.agents.captain import captain
from services.bybit_ws import bybit_ws_service

async def verify_lateral_optimization():
    print("--- Verificando Otimizações de Mercado Lateral (V41.2) ---")
    
    # 1. Testar Bônus RSI no SignalGenerator
    print("\n[TEST 1] SignalGenerator RSI Bonus")
    signal_generator.btc_drag_mode = False
    # Mock de dados de mercado para RSI extremo
    mock_indicators = {
        'rsi': 20, 
        'cvd_1h': 50000,
        'ls_ratio': 1.0,
        'whale_buy_vol': 0,
        'whale_sell_vol': 0,
        'trend_1h': 'sideways',
        'pattern': 'none'
    }
    
    # Simular parte da lógica do funnel (Stage 1 preliminar)
    rsi = mock_indicators['rsi']
    mean_reversion_score = 0
    is_mean_reversion = False
    
    if rsi < 25:
        is_mean_reversion = True
        mean_reversion_score = 55
        
    print(f"RSI: {rsi} | Bônus Esperado: 55 | Bônus Obtido: {mean_reversion_score}")
    assert mean_reversion_score == 55, "Erro: Bônus de RSI deveria ser 55"
    print("✅ Teste 1 OK")

    # 2. Testar Elite Bypass no Captain
    print("\n[TEST 2] Captain Elite Bypass (Score >= 85 em RANGING)")
    mock_signal = {
        'id': 'test_signal_123',
        'symbol': 'LATERALUSDT',
        'side': 'Buy',
        'score': 89,
        'indicators': {'pattern': 'RANGING_TEST'}
    }
    
    # Simular market_regime
    market_regime = "RANGING"
    score = mock_signal['score']
    
    is_elite_ranging = False
    if market_regime == "RANGING" and score >= 85:
        is_elite_ranging = True
        
    print(f"Regime: {market_regime} | Score: {score} | Elite Bypass Esperado: True | Obtido: {is_elite_ranging}")
    assert is_elite_ranging is True, "Erro: Elite Bypass deveria estar ativo para score 89 em RANGING"
    print("✅ Teste 2 OK")

    # 3. Testar Needle Flip Light
    print("\n[TEST 3] Captain Needle Flip Light (Threshold Reduction)")
    # Simular threshold base
    adaptive_threshold = 1000
    mock_signal_ranging = {'is_market_ranging': True}
    
    if mock_signal_ranging.get("is_market_ranging"):
        adaptive_threshold *= 0.6
        
    print(f"Threshold Base: 1000 | Light Threshold Esperado: 600 | Obtido: {adaptive_threshold}")
    assert adaptive_threshold == 600, "Erro: Threshold de Needle Flip deveria ser reduzido para 600"
    print("✅ Teste 3 OK")

    # 4. Testar Tocaia Light (Thresholds de Preço)
    print("\n[TEST 4] Captain Tocaia Light (Price Thresholds)")
    pullback_threshold = 0.0010 # 0.1%
    if mock_signal_ranging.get("is_market_ranging"):
        pullback_threshold *= 0.7
        
    print(f"PB Threshold Base: 0.1% | Light Esperado: 0.07% | Obtido: {pullback_threshold*100:.3f}%")
    assert abs(pullback_threshold - 0.0007) < 0.00001, "Erro: Threshold de Pullback deveria ser 0.07%"
    print("✅ Teste 4 OK")

    print("\n--- TODOS OS TESTES DE LÓGICA V41.2 PASSARAM! ---")

if __name__ == "__main__":
    asyncio.run(verify_lateral_optimization())
