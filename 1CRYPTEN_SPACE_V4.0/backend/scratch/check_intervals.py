import sqlite3

def check_intervals(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT interval FROM klines")
    intervals = cursor.fetchall()
    conn.close()
    return intervals

if __name__ == "__main__":
    db_path = "backtest_data.db"
    intervals = check_intervals(db_path)
    print("Intervals in database:")
    for interval in intervals:
        print(interval[0])
