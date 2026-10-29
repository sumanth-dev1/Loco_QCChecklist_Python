import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint

db_migration_bp = Blueprint('db_migration', __name__)

@db_migration_bp.route('/db_migration', methods=['GET', 'POST'])
def db_migration():
    return "Database migration is now handled automatically when fetching report details.\n<br><br><b>Status:</b> System is up to date!"
