import asyncio
import httpx
from config import settings

async def test_or():
    key = settings.OPENROUTER_API_KEY.strip()
    if not key.startswith("sk-or-v1-"):
        key = f"sk-or-v1-{key}"
        
    print(f"Testing OpenRouter free model with key: {key[:15]}...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "HTTP-Referer": "https://1crypten.space", 
                "X-Title": "1CRYPTEN Space V4.0",
            },
            json={
                "model": "meta-llama/llama-3.3-70b-instruct:free",
                "messages": [
                    {"role": "user", "content": "Oi"}
                ]
            }
        )
        print(response.status_code)
        print(response.json())

if __name__ == "__main__":
    asyncio.run(test_or())
