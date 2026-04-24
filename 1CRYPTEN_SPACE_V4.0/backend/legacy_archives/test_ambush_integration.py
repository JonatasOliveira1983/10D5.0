import asyncio
import logging
import time
import sys
import os

# Ajustar o PATH para encontrar os serviços
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.agents.ambush import ambush_agent
from services.bybit_ws import bybit_ws_service
from services.redis_service import redis_service
from services.signal_generator import signal_generator

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("AmbushTest")

async def run_test():
    logger.info("🚀 Iniciando Teste Simplificado da Lógica Tocaia...")
    
    symbol = "ETHUSDT"
    side = "Buy"
    
    # 1. Mock de dependências externas
    # Mocking price cache
    bybit_ws_service.prices[symbol] = 3100.0
    
    # Mocking Redis for CVD
    async def mock_get_cvd(sym):
        return 50000 # Flow positivo
    redis_service.get_cvd = mock_get_cvd
    
    # Mocking Fibonacci levels in signal_generator
    async def mock_get_fib(sym, tf="60", limit=48):
        return {
            "levels": {
                "0.382": 3000.0, # Alvo da Tocaia
                "0.5": 2950.0
            }
        }
    signal_generator.get_fibonacci_levels = mock_get_fib
    
    # 2. Iniciar a Tocaia (Ambush)
    logger.info(f"🥷 Ativando Tocaia para {symbol} {side}. Alvo Fibo: 3000.0")
    
    # Criar task para a Tocaia
    ambush_task = asyncio.create_task(ambush_agent.execute_ambush(symbol, side, {"id": "TEST_1"}))
    
    await asyncio.sleep(2)
    logger.info(f"📊 Preço atual: {bybit_ws_service.get_current_price(symbol)}. Tocaia em espera...")
    
    # 3. Simular queda de preço para atingir o alvo
    await asyncio.sleep(2)
    logger.info("📉 Simulando queda de preço para 3000.0...")
    bybit_ws_service.prices[symbol] = 3000.0
    
    # 4. Verificar resultado
    try:
        result = await asyncio.wait_for(ambush_task, timeout=10)
        logger.info(f"✅ Resultado da Tocaia: {result}")
        
        if result.get("action") == "TRIGGER":
            logger.info("🏆 TESTE PASSOU: Tocaia disparou corretamente ao atingir o alvo!")
        else:
            logger.error(f"❌ TESTE FALHOU: Ação inesperada {result.get('action')}")
            
    except asyncio.TimeoutError:
        logger.error("❌ TESTE FALHOU: Timeout (a Tocaia não disparou).")

if __name__ == "__main__":
    asyncio.run(run_test())

if __name__ == "__main__":
    asyncio.run(run_test())
