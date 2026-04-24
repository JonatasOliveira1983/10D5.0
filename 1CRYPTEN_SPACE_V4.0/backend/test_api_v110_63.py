import requests
import json

def test_backtest_api():
    url = "http://localhost:8085/api/backtest/run"
    payload = {
        "symbol": "BTCUSDT",
        "timeframes": ["1h"],
        "initial_balance": 100,
        "strategy_toggles": {"lateral_guillotine": True, "sentinel": True}
    }
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        print(f"Status: {response.status_code}")
        if 'results' in data and 'tactical_intel' in data['results']:
            print("SUCCESS: tactical_intel found in response")
            print(json.dumps(data['results']['tactical_intel'], indent=2))
        else:
            print("ERROR: tactical_intel NOT found in response")
            # print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_backtest_api()
