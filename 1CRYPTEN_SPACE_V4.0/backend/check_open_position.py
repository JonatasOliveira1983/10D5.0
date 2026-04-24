import asyncio
import os
import sys

# Helper imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import settings
from services.bybit_rest import bybit_rest_service
from services.bankroll import bankroll_manager

async def main():
    print("--- Simulando Open Position (Paper Mode) ---")
    
    # Simular Ordem no 1000PEPEUSDT (O que faliu)
    # A moeda tava a 0.003798 e o entry salvou como 0.003623
    
    # 1. Mockar as variáveis q vêm do sinal
    signal_data = {
        "indicators": {
            "atr": 0.0001,
            "pattern": "TEST_PATTERN"
        }
    }
    
    # 2. Mockar o PAPER MODE para não gastar dinheiro
    bybit_rest_service.execution_mode = "PAPER"
    print("Bybit Rest Mode:", bybit_rest_service.execution_mode)
    
    # 3. Forçar um slot vazio pra gente testar
    target_slot_id = 4
    symbol = "1000PEPEUSDT"
    
    # Fazer a abertura e ver oq sai no log
    order = await bankroll_manager.open_position(
        symbol=symbol,
        side="Buy",
        pensamento="Teste de Decimais do Antigravity",
        slot_type="SNIPER",
        signal_data=signal_data,
        target_slot_id=target_slot_id
    )
    
    if order:
        print("\n=== Result Order ===")
        print(order)
        print("\nVerifique o DB / Log para ver qual Entry_price foi salvo no Slot 4.")
    else:
        print("\nOrdem falhou (veja log acima).")

if __name__ == "__main__":
    asyncio.run(main())
