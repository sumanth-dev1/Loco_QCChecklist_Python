import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests
from flask import Blueprint, request, jsonify, Response

wfms_proxy_bp = Blueprint('wfms_proxy', __name__)

WFMS_BASE_URL = "https://eg.hbl.in:5105/api"

@wfms_proxy_bp.route('/wfms_proxy', methods=['POST'])
def wfms_proxy():
    action = request.form.get('action', '')

    headers_base = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-app-module': 'WFMS2',
        'x-app-client': 'Wizard'
    }

    try:
        if action == 'login':
            user = request.form.get('user', '')
            pw = request.form.get('pass', '')

            headers = {**headers_base, 'Content-Type': 'application/json'}
            res = requests.post(f"{WFMS_BASE_URL}/login", json={'username': user, 'password': pw}, headers=headers, verify=False, timeout=30)
            return Response(res.text, status=res.status_code, content_type='application/json')

        elif action == 'get_assignments':
            token = request.form.get('token', '')
            headers = {
                **headers_base,
                'Authorization': f'Bearer {token}'
            }
            res = requests.get(f"{WFMS_BASE_URL}/dashboard/assigned-activities", headers=headers, verify=False, timeout=30)
            return Response(res.text, status=res.status_code, content_type='application/json')

        elif action == 'get_activity_details':
            token = request.form.get('token', '')
            activity_id = request.form.get('activityId', '')
            headers = {
                **headers_base,
                'Authorization': f'Bearer {token}'
            }
            res = requests.get(f"{WFMS_BASE_URL}/activity/{activity_id}", headers=headers, verify=False, timeout=30)
            return Response(res.text, status=res.status_code, content_type='application/json')

        return jsonify({'status': False, 'message': 'Unknown action requested.'})
    except Exception as e:
        return jsonify({'status': False, 'message': f'Proxy request failed: {e}'})
