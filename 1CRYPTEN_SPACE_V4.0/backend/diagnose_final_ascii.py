import asyncio
import os
import json
import sys

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from firebase_admin import credentials, firestore, initialize_app, get_app, delete_app

async def main():
    try:
        try: delete_app(get_app())
        except: pass
        
        cred_path = os.path.join(script_dir, "serviceAccountKey.json")
        if not os.path.exists(cred_path):
            print(f"ERROR: No such file or directory: {cred_path}")
            return
            
        initialize_app(credentials.Certificate(cred_path))
        db = firestore.client()
        
        print("DATABASE HISTORY REPORT")
        print("="*30)
        docs = db.collection("trade_history").order_by("timestamp", direction="DESCENDING").limit(10).stream()
        found = False
        for d in docs:
            found = True
            t = d.to_dict()
            print(f"SYMBOL: {t.get('symbol')}")
            print(f"SIDE: {t.get('side')}")
            print(f"PNL: {t.get('pnl')} ({t.get('pnl_percent', 0)}%)")
            print(f"EXIT: {t.get('exit_type', 'UNKNOWN')}")
            reasons = t.get('pensamento', 'N/A')
            # ASCII clean
            reasons = reasons.encode('ascii', 'ignore').decode('ascii')
            print(f"REASON: {reasons[:100]}...")
            print("-" * 20)
            
        if not found:
            print("No trades in history collection.")
            
        print("\nSYSTEM LOGS (RECENT CLOSURES)")
        print("="*30)
        logs = db.collection("system_logs").order_by("timestamp", direction="DESCENDING").limit(30).stream()
        for l in logs:
            msg = l.get("message", "")
            # ASCII clean
            msg = msg.encode('ascii', 'ignore').decode('ascii')
            if any(k in msg.upper() for k in ["CLOSE", "FECHADO", "DELETED", "EMANCIPATED"]):
                print(f"[{l.get('timestamp')}] {l.get('agent')}: {msg}")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
