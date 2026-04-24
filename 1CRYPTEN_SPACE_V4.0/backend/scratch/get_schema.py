import sqlite3

def get_schema(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    schema = cursor.fetchall()
    conn.close()
    return schema

if __name__ == "__main__":
    db_path = "backtest_data.db"
    schema = get_schema(db_path, "klines")
    for col in schema:
        print(col)
