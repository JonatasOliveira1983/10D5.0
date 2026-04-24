import asyncio
import os
from services.bybit_rest import bybit_rest_service

def check_positions():
    print("\n--- POSIÇÕES ATIVAS (MODO PAPER) ---")
    bybit_rest_service._load_paper_state()
    positions = bybit_rest_service.paper_positions
    
    if not positions:
        print("Nenhuma posição ativa no momento.")
    else:
        for p in positions:
            print(f"- {p['symbol']} | Side: {p['side']} | Entry: {p.get('avgPrice')} | Stop: {p.get('stopLoss')}")
    
    print(f"\nSaldo Paper: ${bybit_rest_service.paper_balance:.2f}")

if __name__ == "__main__":
    check_positions()
