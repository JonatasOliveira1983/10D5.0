import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.agents.captain import CaptainAgent
import logging

logging.basicConfig(level=logging.INFO)

# Instanciando capitão mock
captain = CaptainAgent()

async def run_pullback_simulation():
    print("\n\n" + "="*50)
    print("🚀 INICIANDO SIMULAÇÃO PULLBACK V33.0 (CENÁRIO TRUMPUSDT)")
    print("="*50)
    
    # Mockando a leitura do Websocket
    from services.bybit_ws import bybit_ws_service
    
    symbol = "TRUMPUSDT"
    side = "Sell" # Sinal Short do Radar
    
    # Preços mock que o bot vai ler durante o timer de 30s.
    # 1. Abre o sinal no 3.230
    # 2. Faz o "pullback" e vai até 3.246 (Violino - Puxada contra)
    # 3. Retrai para 3.235 (Volta a nosso favor a partir da amarela)
    # Isso deve disparar o BOTE PULLBACK.
    mock_prices_pullback = [
        3.230, 3.230, 3.230, # Inicial (Rompeu)
        3.235, 3.240, 3.245, 3.246, 3.246, # Sobe para a linha amarela contra nós (Pullback contra short)
        3.240, 3.235, 3.235 # Perde força e volta pro meio do caminho
    ]
    
    price_idx = 0
    def mock_get_price(sym):
        nonlocal price_idx
        # Se passar do array mock, continua no ultimo
        if price_idx < len(mock_prices_pullback):
            p = mock_prices_pullback[price_idx]
            price_idx += 1
            return p
        return mock_prices_pullback[-1]
        
    original_get_price = bybit_ws_service.get_current_price
    bybit_ws_service.get_current_price = mock_get_price
    
    print("\n--- TESTE 1: CAÇADOR DE PULLBACK (VIOLINO) ---")
    
    # Executa a função reescrita do capitão com sinal no 3.230
    resultado_pullback = await captain._validate_price_structure(symbol, side, signal_data={"id": "mock_pullback"})
    
    print("\n🎯 Resultado Final do Pullback Hunter:")
    print(resultado_pullback)
    
    # =============== TESTE 2: ANCORAGEM DIRETA ===============
    print("\n\n" + "="*50)
    print("🚀 INICIANDO SIMULAÇÃO ANCORAGEM (DERRETIMENTO DIRETO)")
    print("="*50)
    
    price_idx = 0
    mock_prices_anchorage = [
        3.230, 3.230, 3.230, # Inicial
        3.220, 3.210, 3.200, 3.190, 3.150 # Cai como pedra a favor do short (Muda > 0.25%)
    ]
    
    def mock_get_price_anchorage(sym):
        nonlocal price_idx
        if price_idx < len(mock_prices_anchorage):
            p = mock_prices_anchorage[price_idx]
            price_idx += 1
            return p
        return mock_prices_anchorage[-1]
        
    bybit_ws_service.get_current_price = mock_get_price_anchorage
    
    print("\n--- TESTE 2: ANCORAGEM (Voo direto) ---")
    resultado_ancoragem = await captain._validate_price_structure(symbol, side, signal_data={"id": "mock_anchorage"})
    
    print("\n🎯 Resultado Final Ancoragem:")
    print(resultado_ancoragem)

    # Restaura original
    bybit_ws_service.get_current_price = original_get_price
    
if __name__ == "__main__":
    asyncio.run(run_pullback_simulation())
