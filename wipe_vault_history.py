import firebase_admin
from firebase_admin import credentials, firestore
import os

def clear_trade_history():
    print("Iniciando purgação do Histórico da Vault (trade_history)...")
    cert_path = "1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
    if not os.path.exists(cert_path):
        print("Erro: Credenciais do Firebase não encontradas.")
        return

    try:
        cred = credentials.Certificate(cert_path)
        # Check if already initialized to avoid errors if run in same process
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        # Reference to the trade_history collection
        history_ref = db.collection("trade_history")
        
        # Get all documents
        docs = history_ref.stream()
        
        deleted_count = 0
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1
            
        print(f"Sucesso! {deleted_count} registros fantasmas foram apagados da Vault.")
        print("O Histórico da Vault está 100% zerado para o novo ciclo.")

    except Exception as e:
        print(f"Erro durante a limpeza: {e}")

if __name__ == "__main__":
    clear_trade_history()
