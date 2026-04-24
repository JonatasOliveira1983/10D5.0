import asyncio
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.bankroll import bankroll_manager
from services.firebase_service import firebase_service
from services.bybit_rest import bybit_rest_service
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Test")

async def test_duplicate():
    logger.info("🔥 INICIANDO TESTE SEVERO DE DUPLICIDADE EM MODO PAPER 🔥")
    await firebase_service.initialize()
    await bybit_rest_service.initialize()

    symbol = "DOGEUSDT"
    side = "Buy"

    # Criar duas tasks exatamente no mesmo milissegundo para estressar
    # a concorrência e forçar a falha do Inertia Shield antigo.
    logger.info(f"Disparando 2 ordens simultâneas para {symbol}...")
    
    # Burlar verificação de slots (só para esse teste conseguir chegar no open_position)
    async def mock_can_open(symbol=None, slot_type=None):
        return 4 # Força o uso do Slot 4, ignorando o limite
    bankroll_manager.can_open_new_slot = mock_can_open

    async def open_call(label):
        logger.info(f"[{label}] Enviando ordem...")
        res = await bankroll_manager.open_position(
            symbol=symbol,
            side=side,
            sl_price=0,
            tp_price=0,
            pensamento=f"TESTE_DUPLICATA_{label}",
            slot_type="SWING",
            target_slot_id=1
        )
        logger.info(f"[{label}] Resultado: {'SUCESSO' if res else 'BLOQUEADO'}")

    # Executa ambas ao mesmo tempo
    await asyncio.gather(
        open_call("Tiro 1"),
        open_call("Tiro 2")
    )
    
    logger.info("✅ Fim do Teste. Verifique se apenas 1 slot foi preenchido com DOGEUSDT e o Tiro 2 foi bloqueado pelo Ultimate Guard.")

if __name__ == "__main__":
    asyncio.run(test_duplicate())
