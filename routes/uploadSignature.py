import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
from flask import Blueprint, request, jsonify
from db import get_connection

uploadSignature_bp = Blueprint('uploadSignature', __name__)

@uploadSignature_bp.route('/uploadSignature', methods=['POST'])
def uploadSignature():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                upload_dir = 'uploads/'
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, file.filename).replace('\\', '/')
                file.save(file_path)

                inspector_name = request.form.get('inspector_name')
                inspector_signature = request.form.get('inspector_signature')
                inspector_date = request.form.get('inspector_date')
                approver_name = request.form.get('approver_name')
                approver_signature = request.form.get('approver_signature')
                approver_date = request.form.get('approver_date')

                conn = None
                try:
                    conn = get_connection()
                    cursor = conn.cursor(buffered=True)
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS signatures (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            file_path VARCHAR(255) NULL,
                            inspector_name VARCHAR(255) NULL,
                            approver_name VARCHAR(255) NULL,
                            inspector_signature VARCHAR(255) NULL,
                            approver_signature VARCHAR(255) NULL,
                            inspector_date VARCHAR(50) NULL,
                            approver_date VARCHAR(50) NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    sql = """INSERT INTO signatures 
                             (file_path, inspector_name, approver_name, inspector_signature, approver_signature, inspector_date, approver_date)
                             VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (file_path, inspector_name, approver_name, inspector_signature, approver_signature, inspector_date, approver_date))
                    return jsonify({"success": True, "message": "File uploaded and data saved successfully"})
                except Exception as e:
                    return jsonify({"success": False, "message": f"Failed to save data: {e}"})
                finally:
                    if conn and conn.is_connected():
                        conn.close()

        return jsonify({"success": False, "message": "Failed to upload file"})
    return jsonify({"success": False, "message": "Failed to upload file"})
