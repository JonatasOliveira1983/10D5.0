import re
import os

path = r'c:\Users\spcom\Desktop\10D REAL 4.0\frontend\cockpit.html'
output_path = r'c:\Users\spcom\Desktop\10D REAL 4.0\frontend\app.jsx'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all <script type="text/babel"> blocks
scripts = re.findall(r'<script type="text/babel">(.*?)</script>', content, re.DOTALL)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write('/* Combined JSX from cockpit.html */\n\n')
    for i, script in enumerate(scripts):
        f.write(f'// --- Script {i+1} ---\n')
        # Remove any destruction that might conflict or re-declare
        # But for now, just append
        f.write(script.strip())
        f.write('\n\n')

print(f"Extracted {len(scripts)} scripts to {output_path}")
