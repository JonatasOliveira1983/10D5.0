import asyncio
import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

async def main():
    cred_path = "c:\\Users\\spcom\\Desktop\\10D-3.0\\1CRYPTEN_SPACE_V4.0\\backend\\serviceAccountKey.json"
    if not os.path.exists(cred_path):
        print(f"Error: {cred_path} not found")
        return
        
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    print("=== TRADE HISTORY (Last 20) ===")
    docs = db.collection("trade_history").limit(100).stream()
    
    trades = []
    for doc in docs:
        d = doc.to_dict()
        d['id'] = doc.id
        trades.append(d)
        
    def get_ts(trade):
        return trade.get('timestamp') or trade.get('closed_at') or trade.get('opened_at') or ""
        
    # Standardize timestamp to string for sorting
    for t in trades:
        ts = get_ts(t)
        if isinstance(ts, (int, float)):
             t['sort_ts'] = datetime.fromtimestamp(ts).isoformat()
        else:
             t['sort_ts'] = str(ts)
             
    trades.sort(key=lambda x: x['sort_ts'], reverse=True)
    
    for t in trades[:20]:
        symbol = t.get('symbol', 'N/A')
        side = t.get('side', 'N/A')
        pnl = t.get('pnl', 0)
        roi = t.get('pnl_percent', 0)
        reason = t.get('reason') or t.get('close_reason') or 'N/A'
        slot = t.get('slot_type') or t.get('slot_id') or 'N/A'
        ts = t.get('sort_ts', 'N/A')
        
        safe_reason = str(reason).encode('ascii', 'ignore').decode('ascii')
        
        print(f"[{ts[:19]}] {symbol} {side} ({slot}) | PnL: ${pnl:.4f} ({roi:.2f}%) | Reason: {safe_reason}")

    print("\n=== VAULT STATUS ===")
    vault_doc = db.collection("vault_management").document("current_cycle").get()
    if vault_doc.exists:
        v = vault_doc.to_dict()
        print(f"Cycle: {v.get('cycle_number')} | Wins (Total Mega): {v.get('mega_cycle_wins')}/100")
        print(f"Cycle Wins (1/10): {v.get('cycle_gains_count')}/10 | Total in Cycle: {v.get('total_trades_cycle')}")
        print(f"Profit: ${v.get('cycle_profit', 0):.2f}")
        print(f"Start Bankroll: ${v.get('cycle_start_bankroll', 0):.2f}")
        print(f"Symbols Used: {', '.join(v.get('used_symbols_in_cycle', []))}")
    else:
        print("Vault cycle document not found.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        import traceback
        traceback.print_exc()
