import asyncio
from services.bybit_rest import bybit_rest_service

async def test_balance():
    try:
        balance = await bybit_rest_service.get_wallet_balance()
        print(f"Bybit Wallet Balance: {balance}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_balance())
