import sys, os

# If launched under pythonw.exe, redirect stdout and stderr to avoid NoneType errors
if sys.stdout is None:
    sys.stdout = open(os.path.join(os.path.dirname(__file__), "server.log"), "a", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.path.join(os.path.dirname(__file__), "server_err.log"), "a", encoding="utf-8")

from waitress import serve
from app import app
from database.setup_database import setup_or_migrate

if __name__ == "__main__":
    try:
        # Automatically ensures loco_info is preserved and hhp_loco_info is created with all tables
        setup_or_migrate()
    except Exception as e:
        print(f"Database pre-check notice: {e}")

    print("========================================================")
    print("  LOCO QC PYTHON SERVER STARTING ON PORT 5000")
    print("  Access URL: http://localhost:5000/")
    print("========================================================")
    serve(app, host='0.0.0.0', port=5000)
