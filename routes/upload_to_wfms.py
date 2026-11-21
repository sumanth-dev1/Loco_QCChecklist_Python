import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import hashlib, requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from flask import Blueprint, request, jsonify, session
from db import get_connection, get_hhp_connection

upload_to_wfms_bp = Blueprint('upload_to_wfms', __name__)

WFMS_BASE_URL = "https://eg.hbl.in:5105/api"

@upload_to_wfms_bp.route('/upload-to-wfms', methods=['POST'])
def upload_to_wfms():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access. Please log in.'})

    report_id = request.form.get('reportId')
    activity_id = request.form.get('activityId')
    doc_id = request.form.get('docId')
    wfms_token = request.form.get('wfms_token', '')
    is_hhp = request.form.get('is_hhp') == '1'

    if not all([report_id, activity_id, doc_id, wfms_token]):
        return jsonify({'success': False, 'message': 'Missing required parameters (reportId, activityId, docId, or token).'})

    conn = None
    target_db = 'hhp_loco_info' if is_hhp else 'loco_qc'
    try:
        conn = get_hhp_connection() if is_hhp else get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        cursor.execute("SELECT file_name, last_uploaded_hash FROM report WHERE id = %s", (report_id,))
        report = cursor.fetchone()

        # Fallback to the other database if not found in primary
        if not report:
            conn.close()
            if target_db == 'loco_qc':
                conn = get_hhp_connection()
                target_db = 'hhp_loco_info'
            else:
                conn = get_connection()
                target_db = 'loco_qc'
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT file_name, last_uploaded_hash FROM report WHERE id = %s", (report_id,))
            report = cursor.fetchone()

        if not report:
            return jsonify({'success': False, 'message': 'Report not found in local database.'})

        file_path = os.path.join('uploads', 'reports', report['file_name'])
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'Report file found in DB but missing on disk.'})

        # Calculate SHA256
        with open(file_path, 'rb') as f:
            local_hash = hashlib.sha256(f.read()).hexdigest()

        if report.get('last_uploaded_hash') == local_hash:
            return jsonify({'success': True, 'message': 'Report is already up-to-date in Loco WFMS.'})

        headers = {
            'Authorization': f'Bearer {wfms_token}',
            'x-app-module': 'WFMS2',
            'x-app-client': 'Wizard'
        }

        # Push file directly to /activity/upload
        with open(file_path, 'rb') as f:
            files = {'file': (report['file_name'], f, 'application/pdf')}
            data = {
                'activityId': activity_id,
                'docId': doc_id
            }
            upload_res = requests.post(f"{WFMS_BASE_URL}/activity/upload", headers=headers, data=data, files=files, verify=False, timeout=60)

        res_data = upload_res.json() if upload_res.headers.get('content-type', '').startswith('application/json') else {}

        if upload_res.status_code == 200 and res_data.get('status'):
            try:
                cursor.execute("UPDATE report SET last_uploaded_hash = %s WHERE id = %s", (local_hash, report_id))
            except Exception:
                pass
            return jsonify({'success': True, 'message': 'Report pushed to Loco WFMS successfully!'})
        else:
            error_msg = res_data.get('message') or f"HTTP {upload_res.status_code}: {upload_res.text}"
            return jsonify({'success': False, 'message': f'Loco WFMS Error: {error_msg}'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
