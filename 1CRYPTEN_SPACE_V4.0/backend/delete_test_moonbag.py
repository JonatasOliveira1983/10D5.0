
import asyncio
from services.firebase_service import firebase_service

async def delete_test():
    await firebase_service.initialize()
    try:
        firebase_service.db.collection("moonbags").document("test_moonbag_1").delete()
        print("✅ Moonbag de teste (test_moonbag_1) deletada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao deletar: {e}")

if __name__ == "__main__":
    asyncio.run(delete_test())
