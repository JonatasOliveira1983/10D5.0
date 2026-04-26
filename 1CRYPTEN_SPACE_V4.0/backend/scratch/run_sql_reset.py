import psycopg2
import os
from dotenv import load_dotenv

env_path = r"C:\Users\spcom\Desktop\10D REAL 4.0\1CRYPTEN_SPACE_V4.0\backend\.env"
load_dotenv(env_path, override=True)

def execute_nuclear_reset():
    url = os.getenv("DATABASE_URL")
    if not url:
        print("Error: DATABASE_URL not found!")
        return
        
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgres://", 1)
        
    sql_file = r"C:\Users\spcom\Desktop\10D REAL 4.0\1CRYPTEN_SPACE_V4.0\backend\scratch\nuclear_reset.sql"
    
    with open(sql_file, 'r') as f:
        sql = f.read()
        
    try:
        conn = psycopg2.connect(url)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Executing nuclear reset SQL...")
        cur.execute(sql)
        
        print("Finalizing...")
        cur.execute("SELECT saldo_total FROM banca_status WHERE id = 1")
        banca = cur.fetchone()
        
        print(f"Banca resetada: ${banca[0] if banca else 'N/A'}")
        
        cur.close()
        conn.close()
        print("✅ RESET NUCLEAR CONCLUÍDO COM SUCESSO VIA SQL.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    execute_nuclear_reset()
