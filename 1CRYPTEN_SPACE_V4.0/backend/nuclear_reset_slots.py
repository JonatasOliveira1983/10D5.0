import firebase_admin
from firebase_admin import credentials, firestore, db
import os
import json

# Setup paths
backend_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(backend_dir, "serviceAccountKey.json")
env_path = os.path.join(backend_dir, ".env")

print("=== Starting NUCLEAR RESET of Slots (Clean Mode) ===")

# Load .env for RTDB URL
env_params = {}
if os.path.exists(env_path):
    try:
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    parts = line.strip().split("=", 1)
                    env_params[parts[0]] = parts[1].replace('"', '')
    except Exception as e:
        print(f"Error reading .env: {e}")

db_url = env_params.get("FIREBASE_DATABASE_URL", "")
print(f"Firebase URL: {db_url}")

# Initialize Firebase
if not os.path.exists(cred_path):
    print(f"Error: {cred_path} not found!")
    os._exit(1)

try:
    cred = credentials.Certificate(cred_path)
    # Check if app is already initialized
    try:
        firebase_admin.get_app()
        print("Firebase already initialized, using existing app.")
    except ValueError:
        firebase_admin.initialize_app(cred, {'databaseURL': db_url})
except Exception as e:
    print(f"Failed to initialize Firebase: {e}")
    os._exit(1)

fs = firestore.client()

# 1. Reset Firestore Slots
print("Cleaning Firestore 'slots_ativos'...")
try:
    slots_ref = fs.collection("slots_ativos")
    docs = slots_ref.get()
    for doc in docs:
        print(f"Deleting Firestore Slot {doc.id}")
        slots_ref.document(doc.id).delete()
except Exception as e:
    print(f"Error cleaning Firestore: {e}")

# 2. Reset RTDB Slots
print("Cleaning RTDB 'live_slots'...")
try:
    rtdb_slots_ref = db.reference("live_slots")
    rtdb_slots_ref.delete()
    print("RTDB live_slots deleted.")
except Exception as e:
    print(f"Error cleaning RTDB: {e}")

# 3. Initialize fresh slots (1 to 4)
print("Initializing 4 empty slots...")
empty_slot = {
    "symbol": None,
    "side": None,
    "qty": 0,
    "entry_price": 0,
    "current_stop": 0,
    "status_risco": "LIVRE",
    "pnl_percent": 0,
    "timestamp_last_update": firestore.SERVER_TIMESTAMP
}

for i in range(1, 5):
    try:
        # Firestore
        fs.collection("slots_ativos").document(str(i)).set({"id": i, **empty_slot})
        # RTDB
        db.reference(f"live_slots/{i}").set({"id": i, **empty_slot})
        print(f"Slot {i} initialized.")
    except Exception as e:
        print(f"Error initializing slot {i}: {e}")

# 4. Reset Banca Status
print("Resetting Banca Status to $100...")
try:
    banca_data = {
        "saldo_total": 100.0,
        "configured_balance": 100.0,
        "risco_real_percent": 0,
        "slots_disponiveis": 4,
        "status": "ONLINE",
        "timestamp_last_update": firestore.SERVER_TIMESTAMP
    }
    fs.collection("banca_status").document("status").set(banca_data)
    db.reference("banca_status").set(banca_data)
    print("Banca status reset.")
except Exception as e:
    print(f"Error resetting banca: {e}")

print("NUCLEAR RESET COMPLETE. The system is now clean.")
os._exit(0)
