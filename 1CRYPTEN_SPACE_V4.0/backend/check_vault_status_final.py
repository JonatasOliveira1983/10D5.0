
import firebase_admin
from firebase_admin import credentials, db, firestore
import json
import os

# Certificado local
cert_path = "c:/Users/spcom/Desktop/10D-3.0/1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
if not os.path.exists(cert_path):
    print(f"Erro: Certificado não encontrado em {cert_path}")
    exit(1)

cred = credentials.Certificate(cert_path)
try:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app'
    })
except:
    pass

fs = firestore.client()
rtdb = db.reference()

print("--- STATUS DO COFRE (Firestore) ---")
vault_doc = fs.collection("vault").document("status").get()
if vault_doc.exists:
    vault_data = vault_doc.to_dict()
    print(json.dumps(vault_data, indent=2))
else:
    print("Documento 'vault/status' não encontrado no Firestore.")

print("\n--- STATUS DO SISTEMA (RTDB) ---")
try:
    state = rtdb.child("system_state").get()
    print(json.dumps(state, indent=2))
except Exception as e:
    print(f"Erro ao acessar RTDB system_state: {e}")

print("\n--- BANCA STATUS (Firestore) ---")
banca_doc = fs.collection("banca_status").document("status").get()
if banca_doc.exists:
    banca_data = banca_doc.to_dict()
    print(json.dumps(banca_data, indent=2))
