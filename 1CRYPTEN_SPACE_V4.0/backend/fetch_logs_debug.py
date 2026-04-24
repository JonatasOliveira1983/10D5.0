import asyncio
import os
import sys

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sovereign_service import sovereign_service

async def fetch_logs():
    await sovereign_service.initialize()
    logs = sovereign_service.db.collection('system_logs').order_by('timestamp', direction='DESCENDING').limit(200).stream()
    
    for l in logs:
        msg = l.to_dict().get('message', '')
        if 'LTCUSDT' in msg or 'Margin' in msg or 'DEPLOYING' in msg:
            print(f"[{l.to_dict().get('timestamp')}] {msg}")

if __name__ == "__main__":
    asyncio.run(fetch_logs())
