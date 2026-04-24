import asyncio
import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.bybit_rest import bybit_rest_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LeverageAnalysis")

async def analyze_leverage():
    logger.info("📡 Consultando instrumentos na Bybit...")
    try:
        # Get all linear instruments
        response = await asyncio.to_thread(bybit_rest_service.session.get_instruments_info, category="linear")
        instruments = response.get("result", {}).get("list", [])
        
        total_pairs = len(instruments)
        logger.info(f"📊 Total de pares encontrados: {total_pairs}")
        
        leverage_20x_50x = []
        leverage_under_20x = []
        leverage_above_50x = []
        exact_50x = []
        
        for inst in instruments:
            symbol = inst.get("symbol")
            if not symbol.endswith("USDT"): continue
            
            # Extract max leverage from leverage_filter
            lev_filter = inst.get("leverageFilter", {})
            max_lev_str = lev_filter.get("maxLeverage", "0")
            try:
                max_lev = float(max_lev_str)
            except:
                max_lev = 0
            
            if max_lev == 50.0:
                exact_50x.append(symbol)
                leverage_20x_50x.append(symbol)
            elif 20.0 <= max_lev <= 50.0:
                leverage_20x_50x.append(symbol)
            elif max_lev < 20.0:
                leverage_under_20x.append(symbol)
            else:
                leverage_above_50x.append(symbol)
                
        # Generate Report
        print("\n" + "="*50)
        print("RELATORIO DE ALAVANCAGEM DA FROTA (BYBIT)")
        print("="*50)
        print(f"Total USDT Pairs Analisados: {len(leverage_20x_50x) + len(leverage_under_20x) + len(leverage_above_50x)}")
        print(f"\n- Entre 20x e 50x: {len(leverage_20x_50x)} pares")
        print(f"   L Específicos 50x: {len(exact_50x)} pares")
        print(f"- Abaixo de 20x:     {len(leverage_under_20x)} pares")
        print(f"- Acima de 50x:      {len(leverage_above_50x)} pares (Ex: BTC, ETH)")
        print("="*50)
        
        # Sample of 20x-50x pairs
        sample = leverage_20x_50x[:10]
        print(f"Amostra 20x-50x: {', '.join(sample)}...")
        
    except Exception as e:
        logger.error(f"Erro na análise: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_leverage())
