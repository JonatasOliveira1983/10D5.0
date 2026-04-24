import firebase_admin
from firebase_admin import credentials, db
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(backend_dir, "serviceAccountKey.json")
env_path = os.path.join(backend_dir, ".env")

env_params = {}
with open(env_path, "r") as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            parts = line.strip().split("=", 1)
            env_params[parts[0]] = parts[1].replace('"', '')

db_url = env_params.get("FIREBASE_DATABASE_URL", "")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {'databaseURL': db_url})

print("\n--- RTDB LIVE SLOTS ---")
slots = db.reference("live_slots").get()
print(slots)

print("\n--- RTDB SLOTS (Legacy path?) ---")
slots2 = db.reference("slots").get()
print(slots2)
