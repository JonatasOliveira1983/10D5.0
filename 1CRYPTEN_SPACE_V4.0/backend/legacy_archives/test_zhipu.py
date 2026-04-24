import asyncio
from config import settings
from zhipuai import ZhipuAI

async def test_api():
    key = settings.GLM_API_KEY.strip()
    print(f"Testing with key prefix: {key[:10]}...")
    client = ZhipuAI(api_key=key)
    
    models_to_test = ["glm-4-flash", "glm-4-flashx", "glm-4-plus", "glm-4v-flash", "glm-3-turbo"]
    
    for model in models_to_test:
        try:
            print(f"\n--- Testing model: {model} ---")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Oi"}]
            )
            print(f"✅ Success! Response: {response.choices[0].message.content}")
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
