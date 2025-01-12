import sys
import os

print("Current working directory:", os.getcwd())
print("\nPython path:")
for path in sys.path:
    print(path)

print("\nTrying imports:")
try:
    from app.main import app
    print("Successfully imported app.main")
except Exception as e:
    print("Error importing app.main:", str(e))

try:
    from app.models import database
    print("Successfully imported app.models.database")
except Exception as e:
    print("Error importing app.models.database:", str(e)) 