import os
import sys
from datetime import datetime
import json

# Adjust path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.sovereign_service import get_db

def analyze_vault():
    try:
        db = get_db()
        # Fetch last 10 trades from trade_history
        docs = db.collection('trade_history').order_by('closed_at', direction='DESCENDING').limit(10).stream()
        
        print("=== LATEST TRADES IN VAULT ===")
        found = False
        for d in docs:
            found = True
            data = d.to_dict()
            
            # Formatting timestamp
            closed_at = data.get('closed_at')
            try:
                dt = datetime.fromisoformat(closed_at.replace('Z', '+00:00')) if isinstance(closed_at, str) else closed_at
                date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                date_str = str(closed_at)
                
            symbol = data.get('symbol', 'N/A')
            side = data.get('side', 'N/A')
            pnl = data.get('pnl_percentage', 0)
            reason = data.get('close_reason', 'N/A')
            gen = data.get('genesis_id', 'N/A')
            profit_usd = data.get('profit_usd', 0)
            
            pnl_str = f"+{pnl}%" if pnl > 0 else f"{pnl}%"
            usd_str = f"+${profit_usd:.2f}" if profit_usd > 0 else f"-${abs(profit_usd):.2f}"
            
            print(f"[{date_str}] {symbol} | {side} | {pnl_str} ({usd_str}) | Reason: {reason} | Genesis: {gen}")
            
            # Print events if they exist to understand what happened
            events = data.get('events', [])
            if events:
                for e in events:
                    print(f"   -> {e.get('timestamp')}: {e.get('type')} - {e.get('description')}")
            print("-" * 50)
            
        if not found:
            print("No trades found in the vault.")
    except Exception as e:
        print(f"Error fetching vault data: {e}")

if __name__ == '__main__':
    analyze_vault()
