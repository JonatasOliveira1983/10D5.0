
import firebase_admin
from firebase_admin import credentials, firestore
import json

def audit():
    print("--- AUDITORIA DE INTELIGÊNCIA SNIPER V110.60 ---")
    
    # 1. Init Firebase
    cert_path = "1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
    if not firebase_admin._apps:
        cred = credentials.Certificate(cert_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    # 2. Analisar Slots Ativos
    print("\n[SLOTS ATIVOS]")
    slots = db.collection('slots_ativos').get()
    for s in slots:
        data = s.to_dict()
        symbol = data.get('symbol')
        if symbol:
            print(f"\nSlot {s.id}: {symbol}")
            print(f" - Agente Origem: {data.get('agente_origem')}")
            print(f" - Consensus Score: {data.get('consenso_score')}")
            print(f" - Librarian Audit: {data.get('librarian_audit', 'NÃO ENCONTRADO')}")
            print(f" - DNA Marker: {data.get('asset_dna', 'NÃO ENCONTRADO')}")
            print(f" - Seal: {data.get('quality_label', 'SEM SELO')}")
            print(f" - Timestamp: {data.get('timestamp_entry')}")

    # 3. Analisar Journey Signals (Histórico de Nascimento)
    print("\n[JOURNEY SIGNALS - ORIGEM DOS SINAIS]")
    signals = db.collection('journey_signals').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(10).get()
    for sig in signals:
        sd = sig.to_dict()
        print(f"\nSinal {sd.get('symbol')} ({sd.get('timestamp')})")
        print(f" - Status: {sd.get('status')}")
        print(f" - Consensus: {sd.get('consensus_score')}")
        print(f" - Quality: {sd.get('quality_label')}")
        print(f" - Librarian Data: {sd.get('librarian_consensus', 'NÃO VINCULADO')}")

if __name__ == "__main__":
    audit()
