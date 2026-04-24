import firebase_admin
from firebase_admin import credentials, firestore, db
import os

# Paths
backend_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(backend_dir, "serviceAccountKey.json")
env_path = os.path.join(backend_dir, ".env")

print("--- FINAL SUPER NUKE START ---")

# Load .env
env_params = {}
with open(env_path, "r") as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            env_params[k] = v.replace('"', '')

db_url = env_params.get("FIREBASE_DATABASE_URL", "")
cred = credentials.Certificate(cred_path)

try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred, {'databaseURL': db_url})

fs = firestore.client()
rtdb = db.reference("/")

# Clean Collections
targets = ["slots_ativos", "moonbags", "banca_status"]
for coll in targets:
    print(f"Purging Firestore collection: {coll}")
    docs = fs.collection(coll).get()
    for doc in docs:
        print(f"Deleting doc {doc.id} from {coll}")
        fs.collection(coll).document(doc.id).delete()

# Clean RTDB
rtdb_targets = ["live_slots", "moonbag_vault", "banca_status"]
for path in rtdb_targets:
    print(f"Purging RTDB path: {path}")
    rtdb.child(path).delete()

# Re-Initialize empty state
print("Initializing 4 empty slots...")
for i in range(1, 5):
    data = {
        "id": i,
        "symbol": None,
        "side": None,
        "status_risco": "LIVRE",
        "pnl_percent": 0,
        "entry_price": 0,
        "current_stop": 0,
        "opened_at": None,
        "fleet_intel": {},
        "unified_confidence": 0
    }
    fs.collection("slots_ativos").document(str(i)).set(data)
    rtdb.child("live_slots").child(str(i)).set(data)

# Re-Initialize Banca
banca = {
    "saldo_total": 100.0,
    "configured_balance": 100.0,
    "status": "ONLINE",
    "slots_disponiveis": 4
}
fs.collection("banca_status").document("status").set(banca)
rtdb.child("banca_status").set(banca)

print("--- SYSTEM FULLY CLEANED ---")
os._exit(0)
