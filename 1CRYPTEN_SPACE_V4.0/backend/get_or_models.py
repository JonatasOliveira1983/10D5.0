import asyncio
import httpx

async def get_free_models():
    async with httpx.AsyncClient() as client:
        res = await client.get("https://openrouter.ai/api/v1/models")
        data = res.json()
        models = data.get("data", [])
        
        free_models = []
        for m in models:
            pricing = m.get("pricing", {})
            if pricing.get("prompt") == "0" and pricing.get("completion") == "0":
                free_models.append(m["id"])
                
        print("Free Models Available:")
        for fm in free_models:
            if "llama" in fm.lower() or "mistral" in fm.lower() or "qwen" in fm.lower() or "zephyr" in fm.lower() or "deepseek" in fm.lower():
                print(fm)

if __name__ == "__main__":
    asyncio.run(get_free_models())
