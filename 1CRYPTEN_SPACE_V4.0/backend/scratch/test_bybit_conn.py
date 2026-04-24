import time
from pybit.unified_trading import HTTP

def test():
    print("Connecting to Bybit...")
    try:
        session = HTTP(testnet=False)
        start = time.time()
        resp = session.get_server_time()
        end = time.time()
        print(f"Success! Server time: {resp.get('result', {}).get('timeSecond')} | Latency: {int((end-start)*1000)}ms")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test()
