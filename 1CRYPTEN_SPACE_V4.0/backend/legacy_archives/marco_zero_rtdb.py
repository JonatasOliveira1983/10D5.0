
import firebase_admin
from firebase_admin import credentials, db

cert_path = "c:/Users/spcom/Desktop/10D-3.0/1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
cred = credentials.Certificate(cert_path)
try:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app'
    })
except:
    pass

rtdb = db.reference()

print("--- PURIFICANDO RTDB (MARCO ZERO) ---")
# Reset Banca
rtdb.child("banca_status/status").update({
    "balance": 100.0,
    "equity": 100.0,
    "total_pnl": 0.0,
    "accumulated_profit": 0.0
})
print("Saldo da Banca resetado para $100.00.")

# Clear History
rtdb.child("trade_history").delete()
print("Histórico de trades deletado.")

# Clear Positions (just in case)
rtdb.child("active_positions").delete()
print("Posições ativas deletadas do RTDB.")

# Reset Vault
rtdb.child("vault/status").update({
    "wins": 0,
    "losses": 0,
    "cycle_profit": 0.0,
    "vault_balance": 0.0
})
print("Cofre/Vault resetado.")

print("\n--- OPERAÇÃO MARCO ZERO CONCLUÍDA ---")
