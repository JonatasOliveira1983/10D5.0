import asyncio
import sys
import os
import time
from collections import deque

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.bybit_ws import bybit_ws_service
from services.agents.captain import captain_agent
from services.firebase_service import firebase_service
from services.bankroll import bankroll_manager

async def test_correlation_shield():
    print("[LOG] Iniciando Teste do Correlation Shield (Pilar 1)...")
    
    # 1. Simular histórico de preços altamente correlacionados (ADA e POL)
    # Criamos um movimento paralelo perfeito
    symbol_a = "POLUSDT"
    symbol_b = "ADAUSDT"
    
    bybit_ws_service.price_history[symbol_a] = deque(maxlen=60)
    bybit_ws_service.price_history[symbol_b] = deque(maxlen=60)
    
    base_price_a = 0.50
    base_price_b = 0.35
    
    for i in range(20):
        # Movimento 100% correlacionado
        factor = 1 + (i * 0.01)
        bybit_ws_service.price_history[symbol_a].append(base_price_a * factor)
        bybit_ws_service.price_history[symbol_b].append(base_price_b * factor)
    
    corr = bybit_ws_service.get_correlation(symbol_a, symbol_b)
    print(f"📊 Correlação calculada entre {symbol_a} e {symbol_b}: {corr}")
    
    # 2. Simular que POLUSDT já está em um slot ativo
    # Mockando o retorno do get_active_slots
    async def mock_get_active_slots(force_refresh=False):
        return [{"slot_id": 1, "symbol": "POLUSDT", "side": "Buy"}]
    
    firebase_service.get_active_slots = mock_get_active_slots
    
    # 3. Simular entrada de sinal para ADAUSDT
    test_signal = {
        "id": "test_signal_corr",
        "symbol": "ADAUSDT",
        "score": 95,
        "side": "Buy",
        "fleet_intel": {"macro": 80, "micro": 80, "smc": 80},
        "indicators": {"pattern": "TEST", "atr": 0.01}
    }
    
    # Mockando funções de saída para não abrir ordem real no Paper/Live durante o teste de lógica
    async def mock_update_signal_outcome(sig_id, outcome, data=None):
        print(f"✅ Resultado do Sinal {sig_id}: {outcome}")
        if "CORRELATION_BLOCK" in outcome:
            print("🎯 TESTE PASSOU: Correlation Shield bloqueou o sinal correlacionado!")
        else:
            print("❌ TESTE FALHOU: O sinal não foi bloqueado.")

    firebase_service.update_signal_outcome = mock_update_signal_outcome
    
    # Executa a lógica do Capitão
    # Precisamos mockar o processamento interno ou chamar o método que contém a trava
    print("🚀 Enviando sinal correlacionado para o Capitão...")
    try:
        # Chamamos o método que agora tem a trava (implementado na V110.62)
        # Como o método é complexo, vamos isolar a parte da trava se possível ou rodar com cautela
        await captain_agent._process_single_signal(test_signal)
    except Exception as e:
        if "CORRELATION_BLOCK" in str(e):
            pass # Esperado se levantasse erro, mas usamos return
        else:
            print(f"Erro no teste: {e}")

if __name__ == "__main__":
    asyncio.run(test_correlation_shield())
