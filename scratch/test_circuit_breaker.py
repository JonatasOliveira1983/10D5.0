import asyncio
import logging
import sys
import os

# Ajusta o path para importar dos services
sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))

from services.resilience import with_circuit_breaker, get_breaker, BreakerState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestBreaker")

@with_circuit_breaker(breaker_name="test_api", failure_threshold=2, recovery_timeout=2.0, max_retries=1, backoff_base=0.1)
async def mock_api_call(fail=False):
    if fail:
        logger.info("  -> Simulando falha na API...")
        raise Exception("API Error 504")
    return "SUCCESS"

async def run_test():
    logger.info("=== INICIANDO TESTE DE CIRCUIT BREAKER ===")
    
    # 1. Teste de Sucesso
    logger.info("\n[TEST 1] Chamada normal (CLOSED)")
    res = await mock_api_call(fail=False)
    logger.info(f"Resultado: {res}")
    
    # 2. Causando Falhas para Abrir o Circuito
    logger.info("\n[TEST 2] Causando falhas para ABRIR o circuito (threshold=2)")
    await mock_api_call(fail=True) # Falha 1
    await mock_api_call(fail=True) # Falha 2 -> Deve abrir
    
    cb = get_breaker("test_api")
    logger.info(f"Estado do Circuito: {cb.state}")
    
    # 3. Tentando chamar com circuito aberto
    logger.info("\n[TEST 3] Chamada com circuito ABERTO (deve retornar fallback None)")
    res = await mock_api_call(fail=False)
    logger.info(f"Resultado (Fallback): {res}")
    
    # 4. Aguardando recuperação (Recovery Timeout = 2s)
    logger.info("\n[TEST 4] Aguardando recuperação (2.5s)...")
    await asyncio.sleep(2.5)
    
    # 5. Teste de Recuperação (HALF-OPEN -> CLOSED)
    logger.info("\n[TEST 5] Chamada de teste para fechar o circuito (HALF-OPEN)")
    res = await mock_api_call(fail=False)
    logger.info(f"Resultado: {res}")
    logger.info(f"Estado final do Circuito: {cb.state}")

if __name__ == "__main__":
    asyncio.run(run_test())
