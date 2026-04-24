
import asyncio
from services.sovereign_service import sovereign_service

async def delete_test():
    await sovereign_service.initialize()
    try:
        sovereign_service.db.collection("moonbags").document("test_moonbag_1").delete()
        print("✅ Moonbag de teste (test_moonbag_1) deletada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao deletar: {e}")

if __name__ == "__main__":
    asyncio.run(delete_test())
