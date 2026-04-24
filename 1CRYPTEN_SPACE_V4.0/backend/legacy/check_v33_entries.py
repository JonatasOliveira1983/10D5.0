import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.sovereign_service import sovereign_service

async def run():
    await sovereign_service.initialize()
    logs = await sovereign_service.get_recent_logs(limit=200)
    
    print("Logs recentes encontrados para PEPE ou SUI:")
    for log in logs:
        msg = log.get("message", "")
        if "PEPE" in msg or "SUI" in msg:
            print(f"[{log.get('timestamp')}] {log.get('level')} | {log.get('agent')}: {msg}")

if __name__ == "__main__":
    asyncio.run(run())
