import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

def get_creds():
    cred_path = r"c:\Users\spcom\Desktop\10D-3.0\1CRYPTEN_SPACE_V4.0\backend\serviceAccountKey.json"
    return credentials.Certificate(cred_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app(get_creds())

db = firestore.client()
docs = db.collection("slots_ativos").stream()
print("Firestore slots_ativos:")
for doc in docs:
    print(f"ID {doc.id}: {doc.to_dict().get('symbol')}")
