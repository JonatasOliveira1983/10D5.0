
import asyncio
import sys
import os
import time
import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb

def sync():
    print("--- INICIANDO SINCRONIA FORCADA DO ORACULO (FIXED) ---")
    
    # 1. Init Firebase
    cert_path = "1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
    if not firebase_admin._apps:
        cred = credentials.Certificate(cert_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app/'
        })
    
    db = firestore.client()
    
    # 2. Dados Estáticos e Simulados (Mesa de Guerra)
    # Em um cenário real, pegaríamos da Bybit, mas aqui vamos forçar os dados que o Almirante viu + correções
    btc_p = 70844.60
    btc_24h = -0.03
    btc_adx = 41.44
    regime = "TRENDING"
    
    context = {
        'btc_price': btc_p,
        'btc_variation_24h': btc_24h,
        'btc_adx': btc_adx,
        'regime': regime,
        'btc_direction': 'DOWN',
        'dominance': 58.2,
        'btc_correlation': 30,
        'status': 'SECURE',
        'last_updated': time.time()
    }
    
    # 3. Firestore
    try:
        db.collection('oracle_context').document('context').set(context)
        print("[OK] Firestore: oracle_context/context Sincronizado!")
    except Exception as e:
        print(f"(X) Erro Firestore: {e}")
        
    # 4. RTDB
    try:
        rtdb.reference('oracle_context').set(context)
        print("[OK] RTDB: oracle_context Sincronizado!")
    except Exception as e:
        print(f"(X) Erro RTDB: {e}")

    print("\n*** SINCRONIA TOTAL V110.60 CONCLUIDA ***")

if __name__ == "__main__":
    sync()
