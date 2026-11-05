import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import urllib.parse
import requests
from flask import Blueprint, request, jsonify, Response
import config

part_details_bp = Blueprint('part_details', __name__)

@part_details_bp.route('/api/part-details', methods=['GET'])
@part_details_bp.route('/api/part-details/<path:part_no>', methods=['GET'])
def get_part_details(part_no=None):
    """
    Directly queries the actual Configuration API (which queries the actual MongoDB database).
    No local files or local fallback databases are used.
    """
    if not part_no:
        part_no = (request.args.get('partNo') or '').strip()
    else:
        part_no = urllib.parse.unquote(str(part_no)).strip()

    if not part_no:
        return jsonify({
            'status': False,
            'matched': False,
            'message': 'Parameter partNo is required.'
        }), 400

    base_url = getattr(config, 'CONFIG_API_BASE_URL', 'http://localhost:6015/api/configuration').rstrip('/')
    headers = {
        'User-Agent': 'Loco-QC-Checklist-Backend',
        'Accept': 'application/json'
    }

    quoted_part = urllib.parse.quote(part_no, safe='')
    target_urls = [
        f"{base_url}/part-details/{quoted_part}",
        f"{base_url}/part-details?partNo={quoted_part}"
    ]

    last_error = None
    for url in target_urls:
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            # Pass through the exact response from the actual Configuration API and actual DB
            out_resp = Response(resp.text, status=resp.status_code, content_type='application/json')
            out_resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            out_resp.headers['Pragma'] = 'no-cache'
            out_resp.headers['Expires'] = '0'
            return out_resp
        except requests.exceptions.RequestException as e:
            last_error = e

    return jsonify({
        'status': False,
        'matched': False,
        'message': f'Unable to connect to Configuration API at {base_url}. Please ensure the service is running.'
    }), 503
