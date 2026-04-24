import os
import sys
import asyncio
import logging
from datetime import datetime, timezone

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("Firebase admin not found. Please install it with 'pip install firebase-admin'")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VAULT-NUKE")

async def nuke_ghosts():
    """
    [V110.25.5] NUCLEAR CLEANUP
    Removes all entries in 'trade_history' collection with PnL == 0.0 or missing PnL.
    """
    try:
        # Initialize Firebase if not already
        if not firebase_admin._apps:
            cred_path = r"C:\Users\spcom\Desktop\10D-3.0\1CRYPTEN_SPACE_V4.0\backend\serviceAccountKey.json"
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Try Environment Variable (Production)
                firebase_env = os.getenv("FIREBASE_CREDENTIALS")
                if firebase_env:
                    import json
                    cred = credentials.Certificate(json.loads(firebase_env))
                    firebase_admin.initialize_app(cred)
                else:
                    # Fallback to default
                    firebase_admin.initialize_app()
        
        db = firestore.client()
        logger.info("🔥 Starting Vault Ghost Cleanup...")
        
        # 1. Fetch all documents in trade_history
        # We fetch all because we want to be thorough, but we could filter by pnl == 0
        docs = db.collection("trade_history").stream()
        
        count = 0
        deleted = 0
        
        for doc in docs:
            count += 1
            data = doc.to_dict()
            pnl = data.get("pnl")
            symbol = data.get("symbol", "UNKNOWN")
            
            # Condition for deletion: PnL is 0.0 (or very close to it)
            # We also delete if pnl field is missing (corrupted)
            should_delete = False
            if pnl is None:
                should_delete = True
            else:
                try:
                    if abs(float(pnl)) < 0.0001:
                        should_delete = True
                except (ValueError, TypeError):
                    should_delete = True
            
            if should_delete:
                logger.info(f"🗑️ Deleting Ghost Trade: {symbol} (PnL: {pnl}) | ID: {doc.id}")
                db.collection("trade_history").document(doc.id).delete()
                deleted += 1
        
        logger.info(f"✅ Cleanup FINISHED.")
        logger.info(f"Total entries scanned: {count}")
        logger.info(f"Total ghosts deleted: {deleted}")
        
    except Exception as e:
        logger.error(f"FATAL Cleanup Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(nuke_ghosts())
