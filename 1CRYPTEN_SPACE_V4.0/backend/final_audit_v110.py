import firebase_admin
from firebase_admin import credentials, db
import json

def final_audit():
    try:
        cred_path = r"c:\Users\spcom\Desktop\10D-3.0\1CRYPTEN_SPACE_V4.0\backend\serviceAccountKey.json"
        cred = credentials.Certificate(cred_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app'
            })
        
        banca = db.reference('banca_status').get()
        slots = db.reference('live_slots').get()
        
        print("\n🔍 RESULTADO DO RESET NUCLEAR (V110.6.2):")
        print(f"💰 BANCA: {json.dumps(banca, indent=2)}")
        print(f"🎰 SLOTS: {json.dumps(slots, indent=2)}")
        
    except Exception as e:
        print(f"❌ ERRO NA AUDITORIA: {e}")

if __name__ == "__main__":
    final_audit()
