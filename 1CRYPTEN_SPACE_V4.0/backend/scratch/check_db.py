
import asyncio
import os
import sys

# Adicionar o diretório backend ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(backend_dir)

print(f"DEBUG: Backend dir: {backend_dir}")

from services.database_service import database_service

async def main():
    await database_service.initialize()
    slots = await database_service.get_active_slots()
    print("--- ACTIVE SLOTS ---")
    for slot in slots:
        print(f"ID: {slot['id']} | Symbol: {slot['symbol']} | Side: {slot['side']} | Leverage: {slot['leverage']}x | PNL: {slot.get('pnl_percent', 0)}% | Type: {slot.get('slot_type', 'N/A')}")
    
    print("\n--- RECENT TRADE HISTORY ---")
    history = await database_service.get_trade_history(limit=20)
    for trade in history:
        leverage = trade.get('data', {}).get('leverage', 'N/A')
        print(f"Symbol: {trade['symbol']} | PNL: {trade['pnl_percent']}% | Leverage: {leverage} | Reason: {trade['close_reason']}")

if __name__ == "__main__":
    asyncio.run(main())
