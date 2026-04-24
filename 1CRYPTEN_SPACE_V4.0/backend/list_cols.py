import asyncio
from services.firebase_service import firebase_service
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def run():
    await firebase_service.initialize()
    if not firebase_service.db:
        print("Erro db")
        return
    cols = [c.id for c in firebase_service.db.collections()]
    print(f"Collections: {cols}")

if __name__ == "__main__":
    asyncio.run(run())
