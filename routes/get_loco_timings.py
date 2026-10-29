import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify
from db import get_connection

get_loco_timings_bp = Blueprint('get_loco_timings', __name__)

@get_loco_timings_bp.route('/get_loco_timings', methods=['GET'])
def get_loco_timings():
    loco_id = (request.args.get('loco_id') or '').strip()
    if not loco_id:
        return jsonify({"success": False, "message": "❌ Missing loco_id"})

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT start_time, completed_time FROM loco WHERE Loco_Id = %s", (loco_id,))
        row = cursor.fetchone()

        if row:
            return jsonify({
                "success": True,
                "start_time": str(row["start_time"]) if row["start_time"] else None,
                "completed_time": str(row["completed_time"]) if row["completed_time"] else None
            })
        else:
            return jsonify({"success": False, "message": "❌ Loco ID not found"})
    except Exception as e:
        return jsonify({"success": False, "message": f"❌ Database error: {e}"})
    finally:
        if conn and conn.is_connected():
            conn.close()
