import os
import sys
import asyncio
import logging

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("Firebase admin not found.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("VAULT-CLEANUP")

async def cleanup_vault():
    """
    [V110.25.9] TOTAL VAULT CLEANUP
    Wipes the trade_history collection and resets the cumulative profit in banca_status.
    """
    try:
        cred_path = r"C:\Users\spcom\Desktop\10D-3.0\1CRYPTEN_SPACE_V4.0\backend\serviceAccountKey.json"
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        logger.info("🧨 Starting TOTAL Vault Wipe...")
        
        # 1. Clear trade_history
        docs = db.collection("trade_history").stream()
        deleted = 0
        for doc in docs:
            db.collection("trade_history").document(doc.id).delete()
            deleted += 1
        logger.info(f"🗑️ Deleted {deleted} trades from history.")
        
        # 2. Reset Banca Status Profit Fields
        banca_ref = db.collection("banca_status").document("status")
        doc = banca_ref.get()
        if doc.exists:
            data = doc.to_dict()
            config_balance = float(data.get("configured_balance", 100.0))
            
            # Reset to configured baseline
            reset_fields = {
                "saldo_total": config_balance,
                "lucro_ciclo": 0.0,
                "lucro_total_acumulado": 0.0,
                "vault_total": 0.0
            }
            banca_ref.update(reset_fields)
            logger.info(f"💰 Banca Profits reset to $0.00 (Saldo: ${config_balance}).")
        
        logger.info("✨ UI History is now CLEAN.")

    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_vault())
