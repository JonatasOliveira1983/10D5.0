import asyncio
import logging
from unittest.mock import MagicMock

# Import components
from services.agents.whale_tracker import whale_tracker
from services.bybit_ws import bybit_ws_service
from services.signal_generator import signal_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestPivot")

async def test_pivot_logic():
    print("\n--- TESTE DE PIVOT ANTI-TRAP (V6.2) FINAL ---")
    
    symbol = "ETHUSDT"
    side = "Buy" # Original Signal (LONG)
    
    # Mock price e CVD para WhaleTracker
    bybit_ws_service.get_current_price = MagicMock(return_value=2500.0)
    signal_generator.calculate_rest_cvd = MagicMock(return_value=200000.0) # Valor alto positivo
    
    print(f"\n1. Simulando sinal original: {symbol} {side}")
    
    # 2. Forçar WhaleTracker a detectar armadilha BULL_TRAP
    # Histórico de Preço fixo e CVD subindo
    whale_tracker.flow_history[symbol] = [
        {'price': 2500.0, 'cvd': 100000, 'ts': 0},
        {'price': 2500.0, 'cvd': 120000, 'ts': 1}
    ]
    
    # O _check_liquidity vai adicionar o 3º ponto com o mock (CVD=200k, Preço=2500)
    # Delta será 200k - 100k = 100k (> 40k), Preço parado (0 < 0.0003) -> BULL_TRAP
    
    whale_result = await whale_tracker._check_liquidity(symbol)
    whale_data = whale_result.get("data", {})
    
    trap_risk = whale_data.get("trap_risk")
    suggested_side = whale_data.get("suggested_side")
    trap_reason = whale_data.get("trap_reason")

    print(f"\n2. Detecção WhaleTracker:")
    print(f"   Trap Risk: {trap_risk}")
    print(f"   Trap Reason: {trap_reason}")
    print(f"   Suggested Side: {suggested_side}")
    
    # 3. Validar a lógica de inversão do Capitão
    is_market_ranging = True
    
    print("\n3. Verificando Inversão (Pivot)...")
    final_side = side
    # O Capitão inverte se for Trap + Ranging + Suggested Side diferente
    if trap_risk and is_market_ranging and suggested_side and suggested_side.lower() != side.lower():
        print(f"   ✅ SUCESSO: Armadilha detectada ({trap_reason}). Inverteria {side} para {suggested_side}!")
        final_side = suggested_side
    else:
        print(f"   ❌ FALHA: Não houve inversão. Risk={trap_risk}, Ranging={is_market_ranging}, Suggested={suggested_side}")
    
    print(f"\nDireção Final do Trade: {final_side}")
    
    if final_side == "Sell":
        print("\n🏆 TESTE PASSOU: O sistema capturou o Bull Trap e inverteu para SHORT!")
    else:
        print("\n💀 TESTE FALHOU.")

if __name__ == "__main__":
    asyncio.run(test_pivot_logic())
