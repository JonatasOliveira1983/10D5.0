import json
from services.sovereign_service import sovereign_service

def check_librarian_rtdb():
    if not sovereign_service.rtdb:
        print("RTDB not connected")
        return
    
    data = sovereign_service.rtdb.child("librarian_intelligence").get()
    print("--- LIBRARIAN RTDB DATA ---")
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    check_librarian_rtdb()
