"""Force Librarian V2 to re-run study by resetting its last_study_time via internal API."""
import requests, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Trigger via the backtest rankings endpoint which forces librarian.rankings refresh
r = requests.get('http://localhost:8085/api/backtest/rankings', timeout=10)
data = r.json()
print(f"Backtest Rankings status: {data.get('status')}")
print(f"Rankings count: {len(data.get('rankings', []))}")

# Now check if the librarian_agent has dna in its in-memory state
# We can't check that from outside, so we just verify the study data
# The real solution is to wait for the next cycle or restart the backend.
print("\nThe Librarian V2 study needs to run again with the new code.")
print("Since the backend was started with the V2 code, the next 2h cycle")
print("will populate dna and nectar_seal in the RTDB.")
print("\nTo force immediate re-study, restart the backend.")
"""Force Librarian V2 to re-run study by resetting its last_study_time via internal API."""
import requests, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Trigger via the backtest rankings endpoint which forces librarian.rankings refresh
r = requests.get('http://localhost:8085/api/backtest/rankings', timeout=10)
data = r.json()
print(f"Backtest Rankings status: {data.get('status')}")
print(f"Rankings count: {len(data.get('rankings', []))}")

# Now check if the librarian_agent has dna in its in-memory state
# We can't check that from outside, so we just verify the study data
# The real solution is to wait for the next cycle or restart the backend.
print("\nThe Librarian V2 study needs to run again with the new code.")
print("Since the backend was started with the V2 code, the next 2h cycle")
print("will populate dna and nectar_seal in the RTDB.")
print("\nTo force immediate re-study, restart the backend.")
