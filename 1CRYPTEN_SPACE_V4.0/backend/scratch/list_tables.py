import sqlite3

def list_tables(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return tables

if __name__ == "__main__":
    db_path = "backtest_data.db"
    tables = list_tables(db_path)
    print("Tables in database:")
    for table in tables:
        print(table[0])
