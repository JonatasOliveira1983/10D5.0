import os
import sys

# Setup paths
base_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.join(base_dir, "services")
sys.path.append(base_dir)

from services.bybit_rest import BybitREST

service = BybitREST()
print(f"DEBUG: PAPER_STORAGE_FILE = {service.PAPER_STORAGE_FILE}")
print(f"DEBUG: FILE EXISTS = {os.path.exists(service.PAPER_STORAGE_FILE)}")
if os.path.exists(service.PAPER_STORAGE_FILE):
    with open(service.PAPER_STORAGE_FILE, 'r') as f:
        print(f"DEBUG: FILE CONTENT = {f.read()}")
