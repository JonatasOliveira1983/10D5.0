import os
import sys
import asyncio
import logging
import time

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("Firebase admin not found. Please install it with 'pip install firebase-admin'")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("DEDUPLICATE")

async def deduplicate():
    """
    [V110.25.6] DEDUPLICATION SCRIPT
    Identifies if a symbol is in two slots and frees the redundant one (higher ID).
    """
    try:
        # Initialize Firebase
        cred_path = r"C:\Users\spcom\Desktop\10D-3.0\1CRYPTEN_SPACE_V4.0\backend\serviceAccountKey.json"
        if not firebase_admin._apps:
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                logger.error(f"Credentials not found at {cred_path}")
                return

        db = firestore.client()
        logger.info("🔍 Scanning slots for duplicates...")
        
        # 1. Fetch active slots
        slots_ref = db.collection("slots_ativos")
        docs = slots_ref.stream()
        
        active_symbols = {} # {symbol: [list of slot_ids]}
        
        for doc in docs:
            data = doc.to_dict()
            slot_id = int(doc.id)
            symbol = data.get("symbol")
            
            if symbol and slot_id in [1, 2, 3, 4]:
                norm_sym = symbol.upper().replace(".P", "")
                if norm_sym not in active_symbols:
                    active_symbols[norm_sym] = []
                active_symbols[norm_sym].append(slot_id)
        
        # 2. Check for duplicates
        duplicates_found = False
        for sym, ids in active_symbols.items():
            if len(ids) > 1:
                duplicates_found = True
                # Keep the one with lowest ID, free others
                ids.sort()
                keep = ids[0]
                to_free = ids[1:]
                
                logger.warning(f"🚨 DUPLICATE DETECTED: {sym} in slots {ids}. Keeping slot {keep}.")
                
                for fid in to_free:
                    logger.info(f"🗑️ Freeing redundant slot {fid} for {sym}...")
                    # Update Firestore to mark slot as LIVRE
                    slots_ref.document(str(fid)).update({
                        "symbol": None,
                        "status_risco": "LIVRE",
                        "pnl_percent": 0.0,
                        "entry_price": 0.0,
                        "current_stop": 0.0,
                        "target_price": 0.0,
                        "qty": 0.0,
                        "timestamp_last_update": time.time()
                    })
        
        if not duplicates_found:
            logger.info("✅ No duplicate symbols found in slots.")
        else:
            logger.info("✨ Deduplication finished successfully.")

    except Exception as e:
        logger.error(f"Error during deduplication: {e}")

if __name__ == "__main__":
    asyncio.run(deduplicate())
