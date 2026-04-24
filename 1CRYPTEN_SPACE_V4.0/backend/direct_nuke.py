import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import db
import os

cred_path = "serviceAccountKey.json"
print("Loading DB config...")

env_params = {}
with open(".env", "r") as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            parts = line.strip().split("=", 1)
            env_params[parts[0]] = parts[1].replace('"', '')

db_url = env_params.get("FIREBASE_DATABASE_URL", "")

print(f"URL: {db_url}")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {'databaseURL': db_url})

fs = firestore.client()
moonbags = fs.collection("moonbags").get()
hype_found = False
for doc in moonbags:
    d = doc.to_dict()
    if d.get("symbol") == "HYPEUSDT":
        print("Found HYPEUSDT in Firestore! Deleting...")
        fs.collection("moonbags").document(doc.id).delete()
        hype_found = True

if not hype_found:
    print("Not found in Firestore.")

print("Checking RTDB...")
rtdb_ref = db.reference("moonbag_vault")
snaps = rtdb_ref.get()
if snaps:
    found_rtdb = False
    for key, val in snaps.items():
        if val.get("symbol") == "HYPEUSDT":
            print(f"Found HYPEUSDT in RTDB ({key})! Deleting...")
            rtdb_ref.child(key).delete()
            found_rtdb = True
    if not found_rtdb:
        print("Not found in RTDB.")
else:
    print("RTDB Empty.")

print("Operation COMPLETE.")
os._exit(0)
