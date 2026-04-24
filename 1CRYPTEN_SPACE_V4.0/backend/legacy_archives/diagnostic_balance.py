import asyncio
import logging
from config import settings
from services.bybit_rest import bybit_rest_service

logging.basicConfig(level=logging.INFO)

async def check():
    await bybit_rest_service.initialize()
    print("--- BYBIT WALLET BALANCE VIA SERVICE ---")
    balance = await bybit_rest_service.get_wallet_balance()
    print("RETURNED BALANCE:", balance)
    
if __name__ == "__main__":
    asyncio.run(check())
