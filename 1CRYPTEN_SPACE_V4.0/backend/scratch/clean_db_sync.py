import psycopg2
import os

DATABASE_URL = "postgresql://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"

def main():
    try:
        print("Conectando ao banco de dados via psycopg2...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("Limpando slot com FARTCOIN...")
        cur.execute("""
            UPDATE slots 
            SET symbol = NULL, status_risco = 'LIVRE', pnl_percent = 0, 
                entry_price = 0, qty = 0, side = NULL,
                order_id = NULL, genesis_id = NULL, timestamp_last_update = extract(epoch from now()),
                pensamento = 'PURGED: Ghost FARTCOIN removed manually'
            WHERE symbol LIKE '%FARTCOIN%'
        """)
        print(f"Slots atualizados: {cur.rowcount}")

        print("Limpando moonbags com FARTCOIN...")
        cur.execute("DELETE FROM moonbags WHERE symbol LIKE '%FARTCOIN%'")
        print(f"Moonbags deletados: {cur.rowcount}")

        print("Limpando Historico Fantasma da Vault (RECOVERY ou $0 PNL)...")
        cur.execute("DELETE FROM trade_history WHERE genesis_id LIKE 'RECOVERY-%'")
        print(f"Trades fantasmas deletados: {cur.rowcount}")

        conn.commit()
        cur.close()
        conn.close()
        print("Banco de dados limpo com sucesso!")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
