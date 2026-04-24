import os

file_path = r"c:\Users\spcom\Desktop\10D-3.0\frontend\cockpit.html"

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Localiza a linha do LogsPage para saber onde comecar a limpeza
start_idx = -1
for i, line in enumerate(lines):
    if "path=\"/chat\" element={<LogsPage />}" in line:
        start_idx = i
        break

if start_idx != -1:
    # Mantem ate a linha do LogsPage e reconstrói o resto
    clean_lines = lines[:start_idx + 1]
    clean_lines.append('                            <Route path="/config" element={<SettingsPage onLogout={handleLogout} theme={theme} setTheme={setTheme} />} />\n')
    clean_lines.append('                            <Route path="/estudo-cpro" element={<CPROStudyPage />} />\n')
    clean_lines.append('                        </Routes>\n')
    clean_lines.append('                        <NavBar onLogout={handleLogout} />\n')
    clean_lines.append('                    </div>\n')
    clean_lines.append('                </BrowserRouter>\n')
    clean_lines.append('            );\n')
    clean_lines.append('        };\n\n')
    clean_lines.append('        createRoot(document.getElementById(\'root\')).render(<App />);\n\n')
    clean_lines.append('        if (\'serviceWorker\' in navigator) {\n')
    clean_lines.append('            navigator.serviceWorker.getRegistrations().then(regs => {\n')
    clean_lines.append('                regs.forEach(reg => reg.unregister());\n')
    clean_lines.append('            });\n')
    clean_lines.append('        }\n')
    clean_lines.append('    </script>\n')
    clean_lines.append('</body>\n')
    clean_lines.append('</html>\n')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)
    print("OK: Cockpit FIXED Successfully!")
else:
    print("ERR: Could not find starting point for fix.")
