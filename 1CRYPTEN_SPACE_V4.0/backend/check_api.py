import requests
import json

base_url = "http://127.0.0.1:8085"

def check_pulse():
    print("\n--- Checking /api/radar/pulse ---")
    try:
        res = requests.get(f"{base_url}/api/radar/pulse")
        if res.ok:
            data = res.json()
            context = data.get("market_context", {})
            print(f"BTC ADX: {context.get('btc_adx')}")
            print(f"BTC Regime: {context.get('btc_regime')}")
            print(f"Signals Count: {len(data.get('signals', []))}")
            if data.get('signals'):
                s = data['signals'][0]
                print(f"Sample Signal ADX: {s.get('indicators', {}).get('adx')}")
        else:
            print(f"Error: {res.status_code}")
    except Exception as e:
        print(f"Failed: {e}")

def check_state():
    print("\n--- Checking /api/system/state ---")
    try:
        res = requests.get(f"{base_url}/api/system/state")
        if res.ok:
            data = res.json()
            print(f"BTC Price: {data.get('btc_price')}")
            print(f"BTC ADX: {data.get('btc_adx')}")
            print(f"System Message: {data.get('message')}")
        else:
            print(f"Error: {res.status_code}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check_pulse()
    check_state()
