import os
BASE_DIR = os.path.dirname(os.path.abspath(r"c:\Users\spcom\Desktop\10D-3.0\1CRYPTEN_SPACE_V4.0\backend\main.py"))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "frontend"))
print(f"FRONTEND_DIR: {FRONTEND_DIR}")
print(f"Does it exist? {os.path.exists(FRONTEND_DIR)}")
if os.path.exists(FRONTEND_DIR):
    print("Files in frontend:")
    print(os.listdir(FRONTEND_DIR))
