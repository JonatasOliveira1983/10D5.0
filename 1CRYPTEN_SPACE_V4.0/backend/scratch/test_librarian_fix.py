import asyncio
import logging
import sys
import os

# Ajusta o path para importar os serviços
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestFix")

async def test_librarian_study():
    from services.agents.librarian import librarian_agent
    from services.backtest.data_extractor import init_db, download_klines
    
    logger.info("Step 1: Initializing Local DB...")
    init_db()
    
    symbol = "BTCUSDT"
    logger.info(f"Step 2: Downloading data for {symbol}...")
    # Baixa algumas klines para teste
    download_klines(symbol, "1h", limit=100)
    download_klines(symbol, "4h", limit=50)
    
    logger.info("Step 3: Running Librarian Market Study (Single Pair)...")
    # Mock monitored pairs to only test BTC
    try:
        from services.bybit_ws import bybit_ws_service
        bybit_ws_service.active_symbols = {symbol}
    except:
        pass
        
    # Executa o estudo
    await librarian_agent.perform_full_market_study()
    
    if symbol in librarian_agent.asset_dna:
        dna = librarian_agent.asset_dna[symbol]
        logger.info(f"✅ SUCCESS! Librarian analyzed {symbol}.")
        logger.info(f"DNA Result: {dna}")
    else:
        logger.error(f"❌ FAILED! Librarian DNA for {symbol} is missing.")
        # Se falhou, os rankings estarão vazios
        logger.error(f"Rankings count: {len(librarian_agent.rankings)}")

async def main():
    try:
        await test_librarian_study()
    except Exception as e:
        logger.error(f"Test crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
