
import sys
import os
sys.path.append(os.getcwd())
from services.database_service import Slot
import inspect

print("Slot attributes:", [a for a in dir(Slot) if not a.startswith('__')])
print("Slot constructor signature:", inspect.signature(Slot.__init__))
