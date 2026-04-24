
import sys

log_file = r'c:\Users\spcom\Desktop\10D REAL 4.0\1CRYPTEN_SPACE_V4.0\backend\backend_live.log'

try:
    with open(log_file, 'rb') as f:
        # Seek to the end
        f.seek(0, 2)
        size = f.tell()
        # Read last 10000 bytes
        f.seek(max(0, size - 10000))
        content = f.read()
        
    # Try multiple encodings
    for enc in ['utf-16', 'utf-16le', 'utf-8', 'latin-1']:
        try:
            text = content.decode(enc)
            print(f"--- Decoded with {enc} ---")
            print(text[-2000:])
            break
        except:
            continue
except Exception as e:
    print(f"Error: {e}")
