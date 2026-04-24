import asyncio
import sys
sys.path.append('c:\\Users\\spcom\\Desktop\\10D-3.0\\1CRYPTEN_SPACE_V4.0\\backend')
from services.agents.ai_service import ai_service
from services.agents.jarvis_brain import jarvis_brain
from config import settings
import logging

logging.basicConfig(level=logging.DEBUG)

async def t():
    user_message = "oi"
    is_greeting = jarvis_brain.is_simple_greeting(user_message)
    if is_greeting:
        prompt = f"""
        Saudação simples do Almirante: "{user_message}"
        Aja naturalmente, seja breve e não dê relatório do sistema ainda.
        """
        print("MENSAGEM ERA GREETING. CHAMANDO A IA...")
        ans = await ai_service.generate_content(prompt, "SISTEMA")
        print("RESPOSTA DA IA:", ans)

asyncio.run(t())
