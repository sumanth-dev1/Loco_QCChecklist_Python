from waitress import serve
from app import app
from database.setup_database import setup_or_migrate

if __name__ == "__main__":
    try:
        # Automatically ensures loco_info is preserved and hhp_loco_info is created
        setup_or_migrate()
    except Exception as e:
        print(f"Database pre-check notice: {e}")

    print("Starting Waitress server on http://0.0.0.0:5000...")
    serve(app, host='0.0.0.0', port=5000)
