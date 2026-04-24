import asyncio
import sys
sys.path.append('c:\\Users\\spcom\\Desktop\\10D-3.0\\1CRYPTEN_SPACE_V4.0\\backend')
from config import settings
import google.generativeai as genai

async def test_gemini():
    gemini_key = settings.GEMINI_API_KEY.strip()
    genai.configure(api_key=gemini_key)
    
    models = [
        'gemini-2.0-flash-lite-preview-02-05',
        'gemini-1.5-flash',
        'gemini-2.5-flash',
        'gemini-exp-1206',
    ]
    
    for m in models:
        try:
            print(f"Testando {m}...")
            model = genai.GenerativeModel(m)
            response = await asyncio.to_thread(model.generate_content, "Diga apenas 'Conectado'.")
            if response and hasattr(response, 'text'):
                print(f"Sucesso com {m}: {response.text}")
                return
        except Exception as e:
            print(f"Falha em {m}: {e}")

asyncio.run(test_gemini())
