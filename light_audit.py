
import firebase_admin
from firebase_admin import credentials, firestore
import time

def light_audit():
    print("--- LIGHT AUDIT: ESP & ADA ---")
    cert_path = "1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
    if not firebase_admin._apps:
        cred = credentials.Certificate(cert_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    symbols = ['ESPUSDT', 'ADAUSDT']
    
    # Check Slots
    print("\n[VERIFICAÇÃO DE SLOTS]")
    slots = db.collection('slots_ativos').get()
    for s in slots:
        d = s.to_dict()
        if d.get('symbol') in symbols:
            print(f"Slot {s.id}: {d.get('symbol')}")
            print(f" - Agente: {d.get('agente_origem')}")
            print(f" - Score: {d.get('consenso_score')}")
            print(f" - Quality: {d.get('quality_label')}")
            print(f" - Librarian DNA: {d.get('asset_dna', 'N/A')}")
            print(f" - Data Entry: {d.get('timestamp_entry')}")

    # Check Journey Signals
    print("\n[VERIFICAÇÃO DE SINAIS DE ORIGEM]")
    for sym in symbols:
        sigs = db.collection('journey_signals').where('symbol', '==', sym).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).get()
        for sig in sigs:
            sd = sig.to_dict()
            print(f"Sinal {sym}:")
            print(f" - Consensus Score: {sd.get('consensus_score')}")
            print(f" - Librarian Audit: {sd.get('librarian_consensus', 'N/A')}")
            print(f" - Quality Level: {sd.get('quality_label')}")
            print(f" - Pescador Audit: {sd.get('pescador_audit', 'N/A')}")
            print(f" - Whale Sentiment: {sd.get('whale_sentiment', 'N/A')}")

if __name__ == "__main__":
    light_audit()
