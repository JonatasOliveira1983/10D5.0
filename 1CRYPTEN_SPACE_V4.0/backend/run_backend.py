import sys
import os
import subprocess
import signal
import time

print("[INFO] Starting 1CRYPTEN SPACE V17.0 Backend Runner...")

# Certifica-se de que estamos no diretório correto (backend)
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Certifica-se de que nenhum servidor antigo e processpython na porta local
try:
    os.system('taskkill /f /im uvicorn.exe >nul 2>&1')
    os.system('powershell -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -match \'uvicorn\' -and $_.CommandLine -match \'main:app\' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>&1')
    print("[OK] Old processes cleared.")
except:
    pass

time.sleep(1)

# Inicia o servidor uvicorn - Forcing UTF-8 internally if needed
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
    # V33.2: Forces Gunicorn/Local to wipe any old Paper positions on boot
env['FORCE_CLEAN_PAPER'] = 'false'

print("[START] Booting Uvicorn on port 8085...")
try:
    subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8085"], env=env)
except KeyboardInterrupt:
    print("\n[HALT] Server Stopped by User.")
