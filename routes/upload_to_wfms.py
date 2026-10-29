import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os, hashlib, requests
from flask import Blueprint, request, jsonify, session
from db import get_connection

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

    if not all([report_id, activity_id, doc_id, wfms_token]):
        return jsonify({'success': False, 'message': 'Missing required parameters (reportId, activityId, docId, or token).'})

    conn = None
    try:
        conn = get_connection()
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

        # Step 1: Upload file to /upload-file
        with open(file_path, 'rb') as f:
            files = {'file': (report['file_name'], f, 'application/pdf')}
            upload_res = requests.post(f"{WFMS_BASE_URL}/upload-file", headers=headers, files=files, verify=False, timeout=60)

        if upload_res.status_code != 200:
            return jsonify({'success': False, 'message': f'Failed to upload file to WFMS: {upload_res.text}'})

        upload_data = upload_res.json()
        saved_file_id = upload_data.get('fileId') or upload_data.get('data', {}).get('fileId')

        if not saved_file_id:
            return jsonify({'success': False, 'message': 'WFMS upload succeeded but no fileId returned.'})

        # Step 2: Push file metadata to activity doc slot
        body = {
            'activityId': activity_id,
            'docId': doc_id,
            'fileId': saved_file_id
        }
        push_res = requests.post(f"{WFMS_BASE_URL}/activity/upload-qc-file", json=body, headers={**headers, 'Content-Type': 'application/json'}, verify=False, timeout=30)

        if push_res.status_code == 200:
            cursor.execute("UPDATE report SET last_uploaded_hash = %s WHERE id = %s", (local_hash, report_id))
            return jsonify({'success': True, 'message': 'Report successfully uploaded and attached in Loco WFMS!'})
        else:
            return jsonify({'success': False, 'message': f'Attached file failed in WFMS: {push_res.text}'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
