import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from services.bybit_rest import bybit_rest_service

async def view_pos():
    pos = await bybit_rest_service.get_active_positions()
    print('BYBIT POSITIONS:', [ (p['symbol'], p.get('side'), p['size'], float(p.get('avgPrice') or 0)) for p in pos])

asyncio.run(view_pos())
