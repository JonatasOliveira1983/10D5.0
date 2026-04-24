import re
import os

files = [
    r"c:\Users\spcom\Desktop\10D-3.0\frontend\index.html",
    r"c:\Users\spcom\Desktop\10D-3.0\frontend\cockpit.html"
]

sublink_pattern = re.compile(
    r'\{\/\*\s*\[NEW\] Sub-link de Navegação Rápida.+?<\/div>\s*<\/div>',
    re.DOTALL
)

new_button = """{/* Navegação Rápida - Lab Backtest */}
                        <div className="max-w-3xl mx-auto w-full px-4 mb-2 mt-4 flex gap-3 overflow-x-auto no-scrollbar py-2">
                             <Link to="/backtest" className="flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/40 rounded-full hover:bg-primary transition-all group shrink-0 active:scale-95 shadow-lg shadow-primary/5">
                                <span className="material-icons-round text-primary text-sm group-hover:text-black">science</span>
                                <span className="text-[10px] font-black text-primary group-hover:text-black uppercase tracking-widest">Laboratório de Testes</span>
                             </Link>
                        </div>"""

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the block if found
    if 'Sub-link de Navegação Rápida' in content:
        content = sublink_pattern.sub(new_button, content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Replaced quick links in {filepath}")
    else:
        print(f"Pattern not found in {filepath}!")
