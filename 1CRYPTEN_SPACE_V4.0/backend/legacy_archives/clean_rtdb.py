
import firebase_admin
from firebase_admin import credentials, db
import os

def clean_rtdb():
    try:
        cred_path = "serviceAccountKey.json"
        
        if not os.path.exists(cred_path):
            print(f"Erro: {cred_path} não encontrado.")
            return

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app'
            })

        print("--- LIMPANDO RTDB ---")
        
        # Limpar live_slots
        db.reference('live_slots').delete()
        print("✅ live_slots limpo.")
        
        # Limpar tocaias
        db.reference('tocaias').delete()
        print("✅ tocaias limpo.")
        
        # Reset system_state slots_occupied a 0 para forçar re-contagem
        db.reference('system_state/slots_occupied').set(0)
        print("✅ system_state resetado.")

    except Exception as e:
        print(f"Erro ao limpar RTDB: {e}")

if __name__ == "__main__":
    clean_rtdb()
