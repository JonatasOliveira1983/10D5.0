import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.firebase_service import firebase_service

async def get_recent_autopsy():
    print("BUSCANDO AUTOPSIA DE TRADES RECENTES (V81.4)...")
    await firebase_service.initialize()
    
    trades = await firebase_service.get_trade_history(limit=5)
    
    if not trades:
        print("Nenhum trade encontrado no historico.")
        return

    for t in trades:
        print(f"\n--- TRADE: {t.get('symbol')} ({t.get('side')}) ---")
        print(f"PnL: ${t.get('pnl')} ({t.get('pnl_percent')}%)")
        print(f"Motivo Fechamento: {t.get('close_reason')}")
        print(f"ROI Final: {t.get('final_roi')}%")
        print("REPORT:")
        print(t.get('reasoning_report', 'Sem report disponível.'))
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(get_recent_autopsy())
