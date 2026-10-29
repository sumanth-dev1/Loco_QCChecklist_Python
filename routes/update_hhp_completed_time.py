import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime
from flask import Blueprint, request, jsonify
from db import get_hhp_connection, get_connection

update_hhp_completed_time_bp = Blueprint('update_hhp_completed_time', __name__)

@update_hhp_completed_time_bp.route('/update_hhp_completed_time', methods=['POST'])
def update_hhp_completed_time():
    loco_id = (request.form.get('loco_id') or '').strip()
    if not loco_id:
        return jsonify({'success': False, 'message': 'Missing loco_id'}), 400

    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    updated = False
    # Attempt hhp_loco_info first, then fallback to loco_info
    for get_conn_fn in [get_hhp_connection, get_connection]:
        conn = None
        try:
            conn = get_conn_fn()
            cursor = conn.cursor(buffered=True)
            cursor.execute("UPDATE loco SET completed_time = %s WHERE Loco_Id = %s", (current_time, loco_id))
            if cursor.rowcount > 0:
                updated = True
                break
        except Exception:
            pass
        finally:
            if conn and conn.is_connected():
                conn.close()

    return jsonify({
        'success': True,
        'message': 'Completed time updated',
        'completed_time': current_time
    })
