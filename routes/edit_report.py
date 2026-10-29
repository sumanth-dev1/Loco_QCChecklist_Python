import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
from flask import Blueprint, request, render_template_string
from db import get_connection

edit_report_bp = Blueprint('edit_report', __name__)

EDIT_REPORT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Edit Report</title>
</head>
<body>
    <h2>Edit Report</h2>
    <textarea rows="10" cols="50">{{ pdf_text }}</textarea>
    <form action="save_report" method="POST">
        <input type="hidden" name="report_id" value="{{ report_id }}">
        <textarea name="updated_text" rows="10" cols="50">{{ pdf_text }}</textarea><br>
        <button type="submit">Save</button>
    </form>
</body>
</html>
"""

@edit_report_bp.route('/edit_report', methods=['GET'])
def edit_report():
    report_id = request.args.get('report_id')
    pdf_text = ""
    if report_id:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT file_name FROM report WHERE id = %s", (report_id,))
            report = cursor.fetchone()
            if not report:
                return "Report not found."

            pdf_path = os.path.join('uploads', 'reports', report['file_name'])
            if not os.path.exists(pdf_path):
                return "File not found."

            try:
                with open(pdf_path, 'r', encoding='utf-8', errors='ignore') as f:
                    pdf_text = f.read()
            except Exception:
                pdf_text = f"[Binary report file: {report['file_name']}]"
        except Exception as e:
            return f"Error: {e}"
        finally:
            if conn and conn.is_connected():
                conn.close()

    return render_template_string(EDIT_REPORT_HTML, report_id=report_id or '', pdf_text=pdf_text)
