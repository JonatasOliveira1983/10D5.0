import asyncio
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

async def audit_losses():
    print("[AUDIT] Inicializando Conexao Firebase...")
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cred_path = os.path.join(backend_dir, "serviceAccountKey.json")
    
    if not os.path.exists(cred_path):
        print(f"!! Erro: {cred_path} nao encontrado")
        return

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        symbols_to_audit = ["XRPUSDT", "JUPUSDT", "AAVEUSDT", "GALAUSDT", "OPUSDT", "IMXUSDT"]
        
        print("\n--- AUDITANDO ULTIMAS 15 TRADES ---")
        # Fetch last 15 trades from trade_history
        docs = db.collection("trade_history").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(15).stream()
        
        for doc in docs:
            data = doc.to_dict()
            symbol = data.get("symbol")
            pnl = data.get("pnl", 0)
            roi = data.get("final_roi", 0)
            reasoning = data.get("reasoning_report", "N/A")
            close_reason = data.get("close_reason", "N/A")
            
            # Formata timestamp
            ts = data.get("timestamp")
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts, 'strftime') else str(ts)
            
            status = "LOSS" if pnl < 0 else "WIN"
            print(f"\n[{ts_str}] {symbol} | {status} | ROI: {roi}% | Reason: {close_reason}")
            
            # Print report for losses or targeted symbols
            if pnl < 0 or symbol in symbols_to_audit:
                print("-" * 40)
                print("GENESIS/AUDIT REPORT:")
                # Remove common problematic characters for Windows terminal
                clean_reasoning = str(reasoning).encode('ascii', 'ignore').decode('ascii')
                print(clean_reasoning)
                print("-" * 40)

    except Exception as e:
        print(f"!! Erro na auditoria: {e}")

if __name__ == "__main__":
    asyncio.run(audit_losses())
