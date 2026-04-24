import asyncio
import logging
from dotenv import load_dotenv
load_dotenv()
from config import settings
from services.sovereign_service import sovereign_service
from services.bybit_rest import bybit_rest_service

logging.basicConfig(level=logging.INFO)

async def check():
    await bybit_rest_service.initialize()
    
    # 1. Check Bankroll Data
    print("=== BANCA STATUS IN FIREBASE ===")
    banca = await sovereign_service.get_banca_status()
    print(banca)
    
    # 2. Check Recent Trades (last 20)
    print("\n=== RECENT TRADES (RECORD) ===")
    trades = await sovereign_service.get_trade_history(limit=20)
    for t in trades[:10]:
        print(f"[{t.get('timestamp')}] {t.get('symbol')} | {t.get('side')} | PnL: {t.get('pnl', 0)} ({t.get('pnl_percent', 0)}%) | Close Reason: {t.get('reason_for_closure', 'Unknown')} | Entry: {t.get('entry_price')} | Exit: {t.get('exit_price')}")
        
    # 3. Check Bybit Orders history
    print("\n=== BYBIT RECENT EXECUTIONS ===")
    try:
        # Fetch closed PnL from Bybit to see what Bybit registered
        closed_pnl = await asyncio.to_thread(bybit_rest_service.session.get_closed_pnl, category="linear", limit=10)
        pnl_list = closed_pnl.get("result", {}).get("list", [])
        for p in pnl_list:
             print(f"Bybit Closed | {p['symbol']} | {p['side']} | PnL: {p['closedPnl']} | ExecType: {p['execType']} | CreatedAt: {p['createdTime']} | UpdatedAt: {p['updatedTime']}")
    except Exception as e:
        print("Failed Bybit fetch:", e)
        
    # 4. Active Slots in Firebase
    print("\n=== ACTIVE SLOTS ===")
    slots = await sovereign_service.get_active_slots()
    for s in slots:
        print(f"Slot {s.get('id')} | {s.get('symbol')} | {s.get('side')} | Entry: {s.get('entry_price')}")

if __name__ == "__main__":
    asyncio.run(check())
