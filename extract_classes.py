import re

jsx_path = r'c:\Users\spcom\Desktop\10D REAL 4.0\frontend\app.jsx'
output_css = r'c:\Users\spcom\Desktop\10D REAL 4.0\frontend\dist\styles.css'

with open(jsx_path, 'r', encoding='utf-8') as f:
    content = f.read()

classes = set()
matches = re.findall(r'className="([^"]+)"', content)
for m in matches:
    for c in m.split():
        classes.add(c)

# This is a very crude way to get a CSS file, but better than nothing
# Actually, I'll just write a message that the build is in progress
# and provide a version of the HTML that is more robust.

print(f"Found {len(classes)} classes")
