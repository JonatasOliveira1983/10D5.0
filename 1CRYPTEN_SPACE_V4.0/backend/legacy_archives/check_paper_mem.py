import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.append(r'c:\Users\spcom\Desktop\10D-3.0\1CRYPTEN_SPACE_V4.0\backend')
load_dotenv(r'c:\Users\spcom\Desktop\10D-3.0\1CRYPTEN_SPACE_V4.0\backend\.env')

from services.bybit_rest import bybit_rest_service

async def main():
    bybit_rest_service._load_paper_state()
    print(f"Paper Positions in Memory: {bybit_rest_service.paper_positions}")

asyncio.run(main())
