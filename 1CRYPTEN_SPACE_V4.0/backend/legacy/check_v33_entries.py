import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.firebase_service import firebase_service

async def run():
    await firebase_service.initialize()
    logs = await firebase_service.get_recent_logs(limit=200)
    
    print("Logs recentes encontrados para PEPE ou SUI:")
    for log in logs:
        msg = log.get("message", "")
        if "PEPE" in msg or "SUI" in msg:
            print(f"[{log.get('timestamp')}] {log.get('level')} | {log.get('agent')}: {msg}")

if __name__ == "__main__":
    asyncio.run(run())
