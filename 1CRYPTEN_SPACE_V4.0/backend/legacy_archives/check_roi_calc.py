import asyncio
import os
import sys
import json
from decimal import Decimal

# Helper imports from our system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.execution_protocol import execution_protocol
from config import settings

async def main():
    print("--- Testando Cálculo de ROI e Limits ---")
    
    # Exemplo 1: 1000PEPEUSDT
    print("\n--- 1000PEPEUSDT ---")
    entry_pepe = 0.003623
    exit_pepe = 0.003618 # Caiu em Buy => Prejuízo
    side_pepe = "Buy"
    
    roi_pepe = execution_protocol.calculate_roi(entry_pepe, exit_pepe, side_pepe)
    print(f"Entry: {entry_pepe} | Exit: {exit_pepe} | Side: {side_pepe}")
    print(f"Calculated ROI: {roi_pepe:.2f}%")
    
    # Exemplo 2: ONDOUSDT
    print("\n--- ONDOUSDT ---")
    entry_ondo = 0.253
    exit_ondo = 0.2531 # Subiu em Buy => Lucro
    roi_ondo = execution_protocol.calculate_roi(entry_ondo, exit_ondo, "Buy")
    print(f"Entry: {entry_ondo} | Exit: {exit_ondo} | Side: Buy")
    print(f"Calculated ROI: {roi_ondo:.2f}%")
    
    # Exemplo 3: WLDUSDT (Do Log)
    # SL=0.423164, Price=0.4205 (Short: price < sl => alive. Wait, if it hit SL, side is Sell. So current_price >= SL)
    # Log: "SNIPER SL HIT: WLDUSDT.P Price=0.4205 | SL=0.423164 | Phase=SAFE"
    # Wait, se SL é 0.423164 e price é 0.4205, então ele não bateu no SL se for BUY (price < SL bate) 
    # e se for SELL (price > SL bate). Mas 0.4205 é menor que 0.4231.
    print("\n--- WLDUSDT (Do Log) ---")
    entry_wld = 0.3838 # Pego do log pnl anterior
    current_price_wld = 0.4205
    side_wld = "Sell" # Assumindo Short, porque subiu
    roi_wld_sell = execution_protocol.calculate_roi(entry_wld, current_price_wld, "Sell")
    sl_wld = 0.423164
    
    print(f"Entry: {entry_wld} | Current: {current_price_wld} | SL: {sl_wld} | Side: Sell")
    print(f"Calculated ROI (Sell): {roi_wld_sell:.2f}%")
    print(f"Bateu no SL? {'Sim' if current_price_wld >= sl_wld else 'Nao'}")
    
    # Assumindo Buy:
    side_wld2 = "Buy"
    roi_wld_buy = execution_protocol.calculate_roi(entry_wld, current_price_wld, "Buy")
    print(f"Entry: {entry_wld} | Current: {current_price_wld} | SL: {sl_wld} | Side: Buy")
    print(f"Calculated ROI (Buy): {roi_wld_buy:.2f}%")
    print(f"Bateu no SL? {'Sim' if current_price_wld <= sl_wld else 'Nao'}")


if __name__ == "__main__":
    asyncio.run(main())
