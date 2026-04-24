import asyncio
import sys
sys.path.append('c:\\Users\\spcom\\Desktop\\10D-3.0\\1CRYPTEN_SPACE_V4.0\\backend')
from services.agents.ai_service import ai_service
import logging

logging.basicConfig(level=logging.DEBUG)

async def test_fallback():
    # Force GLM to fail quickly or bypass it
    ai_service.glm_backoff_until = 9999999999  # Skip GLM
    ai_service.openrouter_backoff_until = 9999999999 # Skip OpenRouter
    
    print("Testando geracao AI direta via Gemini Fallback...")
    try:
        res = await ai_service.generate_content("Responda apenas 'Conectado'.", system_instruction="Teste")
        print(f"RESULTADO: {res}")
    except Exception as e:
        print(f"ERRO FATAL: {e}")

asyncio.run(test_fallback())
