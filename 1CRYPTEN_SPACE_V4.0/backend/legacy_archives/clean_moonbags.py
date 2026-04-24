import firebase_admin
from firebase_admin import credentials, firestore, db
import os
import json

base_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(base_dir, "serviceAccountKey.json")

print("Carregando credenciais do Firebase...")
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app'
        })
    print("Conectado ao Firebase com sucesso.")
except Exception as e:
    print(f"Erro ao conectar ao Firebase: {e}")
    exit(1)

db_fs = firestore.client()
ref_rtdb = db.reference("moonbag_vault")

print("Lendo Moonbags atuais do Firestore...")
docs = db_fs.collection("moonbags").get()
seen = set()
to_delete = []

for doc in docs:
    data = doc.to_dict()
    sym = data.get("symbol")
    if sym in seen:
        to_delete.append((doc.id, sym))
    elif sym:
        seen.add(sym)

print(f"Encontrados {len(to_delete)} moonbags duplicados.")

for uid, sym in to_delete:
    print(f"Limpando duplicata de {sym} (ID: {uid})")
    db_fs.collection("moonbags").document(uid).delete()
    ref_rtdb.child(uid).delete()

print("Limpeza de duplicadas concluída!!!")
