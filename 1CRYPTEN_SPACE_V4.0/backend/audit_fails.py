import asyncio
from services.firebase_service import firebase_service
from datetime import datetime, timedelta, timezone

async def audit_fails():
    await firebase_service.initialize()
    if not firebase_service.is_active:
        print("Firebase is not active.")
        return

    # Check more signals (last 100)
    signals = await firebase_service.get_recent_signals(limit=100)
    
    now = datetime.now(timezone.utc)
    fail_count = 0
    symbols_failed = {}
    
    print(f"--- Signal Outcome Audit (Last 100) ---")
    for s in signals:
        outcome = s.get('outcome')
        if outcome == "NEEDLE_FLIP_FAIL":
            fail_count += 1
            sym = s.get('symbol')
            symbols_failed[sym] = symbols_failed.get(sym, 0) + 1
            
    print(f"Total NEEDLE_FLIP_FAIL: {fail_count}")
    for sym, count in symbols_failed.items():
        print(f"   {sym}: {count} fails")
        
    # Check if ANY order was actually opened in last 30 mins
    success_count = 0
    for s in signals:
        outcome = s.get('outcome')
        if outcome and outcome not in ['None', 'PICKED', 'NEEDLE_FLIP_FAIL']:
            success_count += 1
            print(f"✅ SUCCESS: {s.get('symbol')} | Outcome: {outcome} | at {s.get('timestamp')}")
            
    if success_count == 0:
        print("No successful executions found in the last 100 signals.")

if __name__ == "__main__":
    asyncio.run(audit_fails())
