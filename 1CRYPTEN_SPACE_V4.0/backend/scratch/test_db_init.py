import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath("c:/Users/spcom/Desktop/10D REAL 4.0/1CRYPTEN_SPACE_V4.0/backend"))

from services.database_service import DatabaseService

async def test_db():
    print("Initializing Database...")
    db = DatabaseService()
    try:
        await db.initialize()
        print("Success! Database initialized.")
        if os.path.exists("local_sniper.db"):
            print(f"File created: local_sniper.db ({os.path.getsize('local_sniper.db')} bytes)")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_db())
