import asyncio
from services.firebase_service import firebase_service
from services.vault_service import vault_service

async def main():
    await firebase_service.initialize()
    await firebase_service.initialize_db()
    
    print("Fetching all trade history...")
    trades = await firebase_service.get_trade_history(limit=5000)
    print(f"Found {len(trades)} trades in history.")
    
    deleted = 0
    for trade in trades:
        doc_id = trade.get("id")
        if doc_id:
            try:
                firebase_service.db.collection("trade_history").document(doc_id).delete()
                deleted += 1
            except Exception as e:
                print(f"Error deleting {doc_id}: {e}")
                
    print(f"Successfully deleted {deleted} records from trade_history.")
    
    print("\nRe-syncing Vault and Banca to $100 base...")
    await firebase_service.update_banca_status({
        "id": "status",
        "saldo_real_bybit": 0,
        "risco_real_percent": 0,
        "slots_disponiveis": 4,
        "lucro_total_acumulado": 0,
        "lucro_ciclo": 0,
        "vault_total": 0,
        "saldo_total": 100.0,
        "configured_balance": 100.0
    })
    print("Database is completely sanitized.")

if __name__ == "__main__":
    asyncio.run(main())
