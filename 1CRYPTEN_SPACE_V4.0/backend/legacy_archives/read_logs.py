import sys
import io

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open("system_output.log", "rb") as f:
    content = f.read().decode("utf-16le")
    # Clean up some common mojibake/emoji if needed for terminal
    print(content[-5000:]) 
