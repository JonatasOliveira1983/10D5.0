import asyncio
import httpx
import google.generativeai as genai
from zhipuai import ZhipuAI
from config import settings
import sys

# Forçar stdout para lidar com caracteres estranhos
def safe_print(msg):
    try:
        print(msg.encode('ascii', 'ignore').decode('ascii'))
    except:
        print("Unprintable message")

async def test_all():
    safe_print("--- IA DIAGNOSTIC V21.1 ---")
    
    or_key = settings.OPENROUTER_API_KEY.strip()
    if not or_key.startswith("sk-or-v1-"): or_key = f"sk-or-v1-{or_key}"
    
    models = [
        "deepseek/deepseek-r1:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "mistralai/mistral-small-3.1-24b-instruct:free",
        "qwen/qwen3-next-80b-a3b-instruct:free"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for m in models:
            try:
                safe_print(f"Testing OpenRouter: {m}")
                res = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {or_key}"},
                    json={"model": m, "messages": [{"role": "user", "content": "Hello"}]}
                )
                safe_print(f"  HTTP: {res.status_code}")
                if res.status_code == 200:
                    text = res.json()['choices'][0]['message']['content'][:20]
                    safe_print(f"  SUCCESS: {text}")
                else:
                    safe_print(f"  FAIL: {res.text[:50]}")
            except Exception as e:
                safe_print(f"  Error: {str(e)[:50]}")

    gem_key = settings.GEMINI_API_KEY.strip()
    if gem_key:
        try:
            safe_print("\nTesting Gemini Models List...")
            genai.configure(api_key=gem_key)
            for m in genai.list_models():
                safe_print(f"  Model: {m.name}")
            
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content("Hello")
            safe_print(f"  SUCCESS: {response.text[:20]}")
        except Exception as e:
            safe_print(f"  FAIL: {str(e)[:50]}")

    glm_key = settings.GLM_API_KEY.strip()
    if glm_key:
        try:
            safe_print("\nTesting GLM...")
            client_z = ZhipuAI(api_key=glm_key)
            response = client_z.chat.completions.create(
                model="glm-4",
                messages=[{"role": "user", "content": "Hello"}]
            )
            safe_print(f"  SUCCESS: {response.choices[0].message.content[:20]}")
        except Exception as e:
            safe_print(f"  FAIL: {str(e)[:50]}")

if __name__ == "__main__":
    asyncio.run(test_all())
