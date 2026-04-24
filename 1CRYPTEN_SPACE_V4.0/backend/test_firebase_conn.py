import asyncio
import os
import sys

# Get absolute path to this script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from services.firebase_service import firebase_service
from firebase_admin import credentials

async def test_conn():
    print(f"CWD: {os.getcwd()}")
    print(f"Current Dir: {current_dir}")
    
    # Force credentials using absolute path
    cred_path = os.path.join(current_dir, "serviceAccountKey.json")
    print(f"Checking for credentials at: {cred_path}")
    
    if os.path.exists(cred_path):
        print("--- Credential file found!")
        try:
            # Manually inject credentials for this test
            # In production it should pick up from config.py
            print("Attempting to initialize Firebase manually...")
            # We override the initialize method's logic slightly for this debug script
            import firebase_admin
            from firebase_admin import firestore, db
            try:
                firebase_admin.get_app()
            except ValueError:
                cred = credentials.Certificate(cred_path)
                # Note: We need the DB URL too. Let's try to get it from .env or config
                from config import settings
                options = {'databaseURL': settings.FIREBASE_DATABASE_URL}
                firebase_admin.initialize_app(cred, options)
            
            firebase_service.db = firestore.client()
            firebase_service.rtdb = db.reference("/")
            firebase_service.is_active = True
            print("--- Firebase initialized successfully in test script!")
            
            # Test a simple write
            print("Testing write to 'system_logs'...")
            doc_ref = firebase_service.db.collection("system_logs").add({
                "agent": "SurgicalReset",
                "message": "Connection test success",
                "timestamp": datetime.datetime.now().isoformat()
            })
            print(f"--- Write success! Doc ID: {doc_ref[1].id}")
            
        except Exception as e:
            print(f"--- Initialization failed: {e}")
    else:
        print("--- Credential file NOT found at the expected path.")

if __name__ == "__main__":
    asyncio.run(test_conn())
