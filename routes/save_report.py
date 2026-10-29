import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request
from db import get_connection

save_report_bp = Blueprint('save_report', __name__)

@save_report_bp.route('/save_report', methods=['POST'])
def save_report():
    if request.method == 'POST':
        report_id = request.form.get('report_id')
        updated_text = request.form.get('updated_text')

        if report_id and updated_text is not None:
            conn = None
            try:
                conn = get_connection()
                cursor = conn.cursor(buffered=True)
                cursor.execute("UPDATE report SET file_content = %s WHERE id = %s", (updated_text, report_id))
                return "Report updated successfully!"
            except Exception as e:
                return f"Error: {e}"
            finally:
                if conn and conn.is_connected():
                    conn.close()
    return ""
