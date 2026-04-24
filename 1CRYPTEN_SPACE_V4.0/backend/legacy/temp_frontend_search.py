import re
import os

filepath = r'C:\Users\spcom\Desktop\10D-3.0\frontend\index.html'

try:
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    print('--- API Endpoints in HTML ---')
    endpoints = set(re.findall(r'fetch\([\'\"](.*?)[\'\"]', html))
    for ep in endpoints:
        print(ep)

    print('\n--- History related context ---')
    for match in re.finditer(r'.{0,80}history.{0,80}', html, re.IGNORECASE):
        print(match.group(0).strip())
except Exception as e:
    print(f"Error reading {filepath}: {e}")
