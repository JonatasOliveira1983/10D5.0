import psycopg2
import sys

sys.stdout.reconfigure(encoding='utf-8')
DATABASE_URL = "postgresql://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"

def main():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    print("Checking slots...")
    cur.execute("SELECT symbol FROM slots WHERE symbol LIKE '%FARTCOIN%'")
    slots = cur.fetchall()
    print("Slots:", slots)

    print("Checking system_state...")
    cur.execute("SELECT data FROM system_state WHERE key = 'paper_engine_state'")
    state = cur.fetchone()
    if state and state[0] and "FARTCOIN" in str(state[0]):
        print("FARTCOIN found in system_state!")
    else:
        print("FARTCOIN NOT found in system_state.")

    conn.close()

if __name__ == "__main__":
    main()
