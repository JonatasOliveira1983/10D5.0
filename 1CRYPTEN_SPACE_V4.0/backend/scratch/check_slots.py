import psycopg2
import os
from dotenv import load_dotenv

env_path = r"C:\Users\spcom\Desktop\10D REAL 4.0\1CRYPTEN_SPACE_V4.0\backend\.env"
load_dotenv(env_path, override=True)

def check_slots():
    url = os.getenv("DATABASE_URL")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgres://", 1)
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        cur.execute("SELECT id, symbol, status_risco FROM slots WHERE symbol IS NOT NULL")
        slots = cur.fetchall()
        for s in slots:
            print(f"Slot {s[0]}: {s[1]} ({s[2]})")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_slots()
