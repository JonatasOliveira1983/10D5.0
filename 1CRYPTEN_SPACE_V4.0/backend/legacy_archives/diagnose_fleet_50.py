import asyncio
import os
import json
import sys

# Core paths
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
        
        print("DIAGNOSTICO: FLEET INTELLIGENCE (50% ISSUE)")
        print("="*40)
        
        # 1. Fetch current slots
        docs = db.collection("slots_ativos").stream()
        for d in docs:
            s = d.to_dict()
            symbol = s.get("symbol")
            if not symbol: continue
            
            print(f"Slot {d.id} ({symbol}):")
            intel = s.get("fleet_intel", {})
            print(f"  - Score Global: {s.get('unified_confidence', 50)}%")
            # Robust extraction of micro/macro/smc/onchain
            macro = intel.get("macro", intel.get("macro_score", 50))
            micro = intel.get("micro", intel.get("micro_score", 50))
            smc = intel.get("smc", intel.get("smc_score", 50))
            onchain = intel.get("onchain", intel.get("onchain_score", 50))
            
            print(f"  - Macro: {macro}%")
            print(f"  - Whale: {micro}%")
            print(f"  - SMC: {smc}%")
            print(f"  - OnChain: {onchain}%")
            print(f"  - OnChain Summary: {intel.get('onchain_summary', 'N/A')}")
            print("-" * 20)
            
        # 2. Check system_logs for FLEET keywords
        print("\nRELEVANT SYSTEM LOGS (LAST 30):")
        logs = db.collection("system_logs").order_by("timestamp", direction="DESCENDING").limit(30).stream()
        for l in logs:
            msg = l.get("message", "")
            if any(k in msg.upper() for k in ["FLEET", "ERROR", "DISPATCH", "TIMEOUT", "FALLBACK"]):
                clean_msg = msg.encode('ascii', 'ignore').decode('ascii')
                print(f"[{l.get('timestamp')}] {l.get('agent')}: {clean_msg}")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
