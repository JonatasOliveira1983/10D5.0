import os

jsx_path = r'c:\Users\spcom\Desktop\10D REAL 4.0\frontend\app.jsx'
sanitized_path = r'c:\Users\spcom\Desktop\10D REAL 4.0\frontend\app_sanitized.jsx'

with open(jsx_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
skip_next = False

# Global Unified Imports/Destructuring
output_lines.append("const { useState, useEffect, useRef, useMemo, useCallback } = React;\n")
output_lines.append("const { createRoot } = ReactDOM;\n")
output_lines.append("const { Route, Link, useLocation, useNavigate, Routes, HashRouter } = ReactRouterDOM;\n\n")

for line in lines:
    # Skip the old destructuring lines to avoid re-declarations
    if 'const { useState' in line and ('= React' in line or '= window' in line):
        continue
    if 'const { createRoot } = ReactDOM' in line:
        continue
    if 'const { Route, Link' in line and 'ReactRouterDOM' in line:
        continue
    if 'const { useState, useEffect, useRef, useMemo, Link, Route, useLocation } = window' in line:
        continue
    
    # Check for the end of the file (mount logic)
    if 'const rootEl = document.getElementById(\'root\')' in line:
        # Wrap the mount logic in a function to be called on load
        output_lines.append("\n// --- Secure Mount Logic ---\n")
        output_lines.append("const startApp = () => {\n")
        output_lines.append(line)
        continue
    
    if 'root.render(<App />)' in line:
        output_lines.append(line)
        output_lines.append("};\n\n")
        output_lines.append("if (document.readyState === 'loading') {\n")
        output_lines.append("    document.addEventListener('DOMContentLoaded', startApp);\n")
        output_lines.append("} else {\n")
        output_lines.append("    startApp();\n")
        output_lines.append("}\n")
        # After this point, we might want to stop or handle the rest carefully
        # But let's see if there is more
        continue

    output_lines.append(line)

with open(sanitized_path, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f"Sanitized JSX saved to {sanitized_path}")
