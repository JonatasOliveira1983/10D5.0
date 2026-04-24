import asyncio
import httpx
import google.generativeai as genai
from config import settings

async def dump_models():
    # Gemini
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY.strip())
        with open('gemini_list.txt', 'w') as f:
            for m in genai.list_models():
                f.write(f"{m.name}\t{m.supported_generation_methods}\n")
    except Exception as e:
        print(f"Gemini Dump Error: {e}")

    # OpenRouter
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get('https://openrouter.ai/api/v1/models')
            if res.status_code == 200:
                with open('or_list.txt', 'w', encoding='utf-8') as f:
                    f.write(res.text)
    except Exception as e:
        print(f"OpenRouter Dump Error: {e}")

if __name__ == "__main__":
    asyncio.run(dump_models())
