import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, session
from db import get_hhp_connection, get_connection

uploadHhpReport_bp = Blueprint('uploadHhpReport', __name__)

@uploadHhpReport_bp.route('/uploadHhpReport', methods=['GET', 'POST'])
def uploadHhpReport():
    conn = None
    try:
        conn = get_hhp_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        # Ensure report table exists in hhp_loco_info
        cursor.execute("""CREATE TABLE IF NOT EXISTS `report` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` VARCHAR(100) NOT NULL,
            `file_name` VARCHAR(255) NOT NULL,
            `upload_date` DATETIME NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")

        if request.method == 'POST':
            user_id = (request.form.get('user_id') or '').strip()
            if not user_id:
                user_id = session.get('username') or session.get('user_id') or 'admin'

            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename != '':
                    upload_dir = os.path.join('uploads', 'reports')
                    os.makedirs(upload_dir, exist_ok=True)
                    file_name = secure_filename(file.filename)
                    # If secure_filename stripped standard naming, fall back to safe basename
                    if not file_name:
                        file_name = os.path.basename(file.filename)
                    file_path = os.path.join(upload_dir, file_name)
                    file.save(file_path)

                    sql = "INSERT INTO report (user_id, file_name, upload_date) VALUES (%s, %s, NOW())"
                    cursor.execute(sql, (user_id, file_name))
                    return jsonify({'success': True, 'message': 'HHP Report uploaded successfully.'})

            return jsonify({'success': False, 'message': 'File upload error: POST max size exceeded or no file'})

        elif request.method == 'GET':
            user_id = request.args.get('user_id')
            role = session.get('role', 'user')

            # Check role if user_id provided
            if user_id:
                try:
                    auth_conn = get_connection()
                    auth_cur = auth_conn.cursor(dictionary=True, buffered=True)
                    auth_cur.execute("SELECT role FROM loginpage WHERE username = %s", (user_id,))
                    u = auth_cur.fetchone()
                    if u and u.get('role'):
                        role = u['role']
                    auth_conn.close()
                except Exception:
                    pass

            if role == 'admin' or not user_id:
                sql = "SELECT id, user_id, file_name, upload_date FROM report ORDER BY upload_date DESC"
                cursor.execute(sql)
            else:
                sql = "SELECT id, user_id, file_name, upload_date FROM report WHERE user_id = %s ORDER BY upload_date DESC"
                cursor.execute(sql, (user_id,))

            reports = cursor.fetchall()
            for r in reports:
                if r.get('upload_date'):
                    r['upload_date'] = str(r['upload_date'])

            return jsonify({'success': True, 'reports': reports})

        return jsonify({'success': False, 'message': 'Invalid request method.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database connection failed: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
