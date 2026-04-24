import asyncio
import os
import sys

sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))
from services.firebase_service import firebase_service

async def check():
    await firebase_service.initialize()
    if not firebase_service.db:
        print("Firebase Offline")
        return
        
    print("--- SLOTS ---")
    slots = await firebase_service.get_active_slots()
    if not slots:
        print("Nenhum slot ativo.")
    for s in slots:
        print(f"Slot {s['id']}: {s.get('symbol')} | {s.get('side')} | {s.get('status_risco')}")
        
    print("\n--- TRADE HISTORY (Last 5) ---")
    docs = firebase_service.db.collection("trade_history").order_by("timestamp", direction="DESCENDING").limit(5).get()
    for d in docs:
        t = d.to_dict()
        print(f"{t.get('timestamp')}: {t.get('symbol')} | {t.get('side')} | PnL: {t.get('pnl')} | ROI: {t.get('pnl_percent')}")

    print("\n--- SEARCH FARTCOIN ---")
    docs = firebase_service.db.collection("trade_history").where("symbol", "==", "FARTCOINUSDT").get()
    if not docs:
        # Try without USDT
        docs = firebase_service.db.collection("trade_history").where("symbol", "==", "FARTCOIN").get()
        
    if not docs:
        print("FARTCOIN não encontrado no histórico.")
    for d in docs:
        t = d.to_dict()
        print(f"FARTCOIN Trade: {t.get('timestamp')} | PnL: {t.get('pnl')} | Status: {t.get('status')}")

if __name__ == "__main__":
    asyncio.run(check())
