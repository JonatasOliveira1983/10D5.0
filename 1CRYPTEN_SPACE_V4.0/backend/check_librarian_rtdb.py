import json
from services.firebase_service import firebase_service

def check_librarian_rtdb():
    if not firebase_service.rtdb:
        print("RTDB not connected")
        return
    
    data = firebase_service.rtdb.child("librarian_intelligence").get()
    print("--- LIBRARIAN RTDB DATA ---")
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    check_librarian_rtdb()
