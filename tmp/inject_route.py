import re

files = [
    r"c:\Users\spcom\Desktop\10D-3.0\frontend\index.html",
    r"c:\Users\spcom\Desktop\10D-3.0\frontend\cockpit.html"
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The existing routes end with </Routes> or there's a `<Route path="/config" ... />`
    
    # 1. Clean up old CPRO route if it still exists
    content = re.sub(r'<Route\s+path="/estudo-cpro".+?/>', '', content)

    # 2. Add backtest route if it's not present
    if '<Route path="/backtest"' not in content:
        # Find path="/config"
        content = re.sub(r'(<Route\s+path="/config"\s+element=\{<SettingsPage[^>]+>\}\s*/>)',
                         r'\1\n                                <Route path="/backtest" element={<BacktestLab />} />', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Injected routes successfully!")
