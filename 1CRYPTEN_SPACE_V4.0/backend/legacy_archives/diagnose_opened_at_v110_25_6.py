import os
import sys
import asyncio
import logging
import time

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("Firebase admin not found.")
    sys.exit(1)

async def diagnose():
    try:
        cred_path = r"C:\Users\spcom\Desktop\10D-3.0\1CRYPTEN_SPACE_V4.0\backend\serviceAccountKey.json"
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print("\n=== DIAGNÓSTICO DE SLOTS ATIVOS (V110.25.6) ===")
        
        for i in range(1, 5):
            doc = db.collection("slots_ativos").document(str(i)).get()
            if doc.exists:
                data = doc.to_dict()
                symbol = data.get("symbol", "LIVRE")
                opened_at = data.get("opened_at")
                timestamp_last = data.get("timestamp_last_update")
                
                status = "OK" if symbol != "LIVRE" else "VAZIO"
                
                print(f"Slot {i}: {symbol}")
                print(f"  - Opened At: {opened_at}")
                print(f"  - Last Update: {timestamp_last}")
                
                if symbol != "LIVRE":
                    if opened_at:
                        age = time.time() - float(opened_at)
                        print(f"  - Idade: {age/60:.1f} minutos")
                        if age < 900:
                            print(f"  - [🛡️ PROTEGIDO]: Grace Period (15m) ativo.")
                        else:
                            print(f"  - [🔥 EXPOSTO]: Fora do Grace Period.")
                    else:
                        print(f"  - [⚠️ RISCO]: opened_at ausente! Pode ser purgado pelo GhostBuster se o BybitREST falhar.")
            else:
                print(f"Slot {i}: DOCUMENTO NÃO ENCONTRADO")
        
        print("============================================\n")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose())
