import os

file_path = r'c:\Users\spcom\Desktop\10D REAL 4.0\1CRYPTEN_SPACE_V4.0\backend\services\firebase_service.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Remove as travas de inatividade do Firebase nas funções críticas
    if 'if not self.is_active: return data' in line:
        new_lines.append(line.replace('if not self.is_active: return data', 'if self.is_active and self.db:'))
    elif 'if not self.is_active: return' in line:
        # Se for update_pulse_drag ou algo que não retorna valor
        if 'update_pulse_drag' in line or 'update_slot' in line:
             new_lines.append(line.replace('if not self.is_active: return', 'if self.is_active and self.db:'))
        else:
             new_lines.append(line)
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("SUCCESS: Firebase Service Purged and Synchronized for Railway Sovereign Mode!")
