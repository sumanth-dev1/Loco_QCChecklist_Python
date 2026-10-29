import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
from flask import Blueprint, request, jsonify, session
from db import get_connection

uploadReport_bp = Blueprint('uploadReport', __name__)

@uploadReport_bp.route('/uploadReport', methods=['GET', 'POST'])
def uploadReport():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        if request.method == 'POST':
            user_id = (request.form.get('user_id') or '').strip()
            if not user_id:
                user_id = session.get('username') or session.get('user_id') or 'admin'

            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename != '':
                    upload_dir = os.path.join('uploads', 'reports')
                    os.makedirs(upload_dir, exist_ok=True)
                    file_name = file.filename
                    file_path = os.path.join(upload_dir, file_name)
                    file.save(file_path)

                    sql = "INSERT INTO report (user_id, file_name, upload_date) VALUES (%s, %s, NOW())"
                    cursor.execute(sql, (user_id, file_name))
                    return jsonify({'success': True, 'message': 'File uploaded and report saved to database.'})

            return jsonify({'success': False, 'message': 'File upload error: POST max size exceeded or no file'})

        elif request.method == 'GET':
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'message': 'Missing user_id. Cannot fetch reports.'})

            cursor.execute("SELECT role FROM loginpage WHERE username = %s", (user_id,))
            user = cursor.fetchone()

            if not user:
                return jsonify({'success': False, 'message': 'User not found.'})

            if user['role'] == 'admin':
                sql = "SELECT r.id as report_id, r.file_name, r.upload_date, l.username, l.role FROM report r JOIN loginpage l ON r.user_id = l.username"
                cursor.execute(sql)
            else:
                sql = "SELECT id as report_id, file_name, upload_date FROM report WHERE user_id = %s"
                cursor.execute(sql, (user_id,))

            reports = cursor.fetchall()
            for r in reports:
                if r.get('upload_date'):
                    r['upload_date'] = str(r['upload_date'])

            return jsonify({'success': True, 'reports': reports})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database connection failed: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
