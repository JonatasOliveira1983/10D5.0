import sys
import os
import asyncio
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import settings

logging.basicConfig(level=logging.DEBUG)

from services.agents.ai_service import ai_service

async def test_ai():
    print(f"OpenRouter Key configured: {bool(ai_service.openrouter_key)}")
    print(f"OpenRouter Backoff: {ai_service.openrouter_backoff_until}")
    res = await ai_service.generate_content("Oi")
    print(f"Result: {res}")

if __name__ == "__main__":
    asyncio.run(test_ai())
