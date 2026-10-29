import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify
from db import get_connection

get_hhp_loco_timings_bp = Blueprint('get_hhp_loco_timings', __name__)

@get_hhp_loco_timings_bp.route('/get_hhp_loco_timings', methods=['GET'])
def get_hhp_loco_timings():
    loco_id = (request.args.get('loco_id') or '').strip()
    if not loco_id:
        return jsonify({"success": False, "message": "❌ Missing loco_id"})

    for db_name in ["hhp_loco_info", "loco_info"]:
        conn = None
        try:
            conn = get_connection(database=db_name)
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT start_time, completed_time FROM loco WHERE Loco_Id = %s", (loco_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                st = row.get("start_time")
                ct = row.get("completed_time")
                return jsonify({
                    "success": True,
                    "start_time": st.strftime('%Y-%m-%d %H:%M:%S') if hasattr(st, 'strftime') else (str(st) if st else None),
                    "completed_time": ct.strftime('%Y-%m-%d %H:%M:%S') if hasattr(ct, 'strftime') else (str(ct) if ct else None)
                })
        except Exception:
            if conn and conn.is_connected():
                conn.close()

    return jsonify({"success": False, "message": "❌ Loco ID not found"})
