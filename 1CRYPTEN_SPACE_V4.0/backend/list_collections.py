import firebase_admin
from firebase_admin import credentials, firestore
import os

def list_collections():
    cred_path = "serviceAccountKey.json"
    if not os.path.exists(cred_path):
        print(f"Error: {cred_path} not found")
        return

    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass

    db = firestore.client()
    collections = db.collections()
    for coll in collections:
        print(f"Collection: {coll.id}")

if __name__ == "__main__":
    list_collections()
