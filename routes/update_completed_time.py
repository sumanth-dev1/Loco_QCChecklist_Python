import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime, zoneinfo
from flask import Blueprint, request, jsonify
from db import get_connection

update_completed_time_bp = Blueprint('update_completed_time', __name__)

@update_completed_time_bp.route('/update_completed_time', methods=['POST'])
def update_completed_time():
    loco_id = (request.form.get('loco_id') or '').strip()
    if not loco_id:
        return jsonify({"success": False, "message": "❌ Missing loco_id"})

    current_time = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("UPDATE loco SET completed_time = %s WHERE Loco_Id = %s", (current_time, loco_id))
        return jsonify({"success": True, "message": "✅ Completed time updated"})
    except Exception:
        return jsonify({"success": False, "message": "❌ Update failed"})
    finally:
        if conn and conn.is_connected():
            conn.close()
