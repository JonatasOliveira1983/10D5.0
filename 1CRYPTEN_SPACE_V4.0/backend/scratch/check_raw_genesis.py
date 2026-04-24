import firebase_admin
from firebase_admin import credentials, firestore
import json

def check_raw_genesis(doc_id):
    cred_path = "c:\\Users\\spcom\\Desktop\\10D REAL 4.0\\1CRYPTEN_SPACE_V4.0\\backend\\serviceAccountKey.json"
    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
    except:
        pass
        
    db = firestore.client()
    doc = db.collection("orders_genesis").document(doc_id).get()
    if doc.exists:
        print(f"--- RAW GENESIS: {doc_id} ---")
        print(json.dumps(doc.to_dict(), indent=2, default=str))
    else:
        print(f"Document {doc_id} not found.")

if __name__ == "__main__":
    check_raw_genesis("BLZ-PAPER-BIOUSDT-123-BIOU")
