import re

files = [
    r"c:\Users\spcom\Desktop\10D-3.0\frontend\index.html",
    r"c:\Users\spcom\Desktop\10D-3.0\frontend\cockpit.html"
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove sub-link navigation
    sublink_pattern = re.compile(r'\s*\{\/\*\s*\[NEW\] Sub-link de Navegação Rápida.+?<\/div>\s*<\/div>', re.DOTALL)
    content = sublink_pattern.sub('', content)

    # Remove CPRO study system
    cpro_pattern = re.compile(r'\s*\/\/\s*\[NEW\] CPRO Study System - 2026 Transition.+?(?=\s*\/\/\s*6\. Takeoff Checklist Modal)', re.DOTALL)
    content = cpro_pattern.sub('\n\n\n', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Cleaned {len(files)} files!")
