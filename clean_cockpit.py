import re

path = r'c:\Users\spcom\Desktop\10D REAL 4.0\frontend\cockpit.html'
output_path = r'c:\Users\spcom\Desktop\10D REAL 4.0\frontend\cockpit_clean.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove Tailwind and Babel CDNs
content = re.sub(r'<script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.24.5/babel.min.js\?v=110.15.1"></script>', '', content)
content = re.sub(r'<script src="https://cdn.tailwindcss.com\?plugins=forms,typography"></script>', '', content)

# 2. Add local links in head (before </head>)
head_links = '\n    <link rel="stylesheet" href="dist/styles.css">\n    <script defer src="dist/app.js"></script>\n'
content = content.replace('</head>', head_links + '</head>')

# 3. Remove inline <style> block (the main one)
content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)

# 4. Remove all <script type="text/babel"> blocks
content = re.sub(r'<script type="text/babel">.*?</script>', '', content, flags=re.DOTALL)

# 5. Remove the tailwind.config script in head
content = re.sub(r'<script>\s*tailwind.config =.*?</script>', '', content, flags=re.DOTALL)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Cleaned cockpit saved to {output_path}")
