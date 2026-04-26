import psycopg2
import os
from dotenv import load_dotenv

env_path = r"C:\Users\spcom\Desktop\10D REAL 4.0\1CRYPTEN_SPACE_V4.0\backend\.env"
load_dotenv(env_path, override=True)

def check_state_sync():
    url = os.getenv("DATABASE_URL")
    print(f"Debug URL: {url[:20] if url else 'None'}...")
    
    if not url or url == "<sua_url_do_postgres>":
        print("Error: DATABASE_URL not loaded correctly!")
        return
        
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgres://", 1)
        
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        
        cur.execute("SELECT saldo_total FROM banca_status WHERE id = 1")
        banca = cur.fetchone()
        
        cur.execute("SELECT COUNT(*) FROM slots WHERE symbol IS NOT NULL")
        slots_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM trade_history")
        history_count = cur.fetchone()[0]
        
        print(f"Banca (Saldo): {banca[0] if banca else 'None'}")
        print(f"Slots Ativos: {slots_count}")
        print(f"Historico Vault (Total): {history_count}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_state_sync()
