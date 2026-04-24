import asyncio
from services.sovereign_service import sovereign_service
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def run():
    await sovereign_service.initialize()
    if not sovereign_service.db:
        print("Erro db")
        return
    cols = [c.id for c in sovereign_service.db.collections()]
    print(f"Collections: {cols}")

if __name__ == "__main__":
    asyncio.run(run())
