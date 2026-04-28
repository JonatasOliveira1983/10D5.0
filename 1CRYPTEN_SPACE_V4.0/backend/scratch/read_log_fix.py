import os

def read_logs():
    log_file = "c:\\Users\\spcom\\Desktop\\10D REAL 4.0\\1CRYPTEN_SPACE_V4.0\\backend\\backend_v110_173.log"
    if not os.path.exists(log_file):
        print("Log file not found.")
        return

    print(f"Reading {log_file}...")
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        
    print(f"Total lines: {len(lines)}")
    # Find last 500 lines
    last_lines = lines[-500:]
    
    keywords = ["BLITZ", "SWING", "GHOST", "Slot", "CaptainAgent", "BankrollManager"]
    for line in last_lines:
        if any(kw in line for kw in keywords):
            print(line.strip())

if __name__ == "__main__":
    read_logs()
