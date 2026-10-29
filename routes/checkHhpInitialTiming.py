import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime, zoneinfo
from flask import Blueprint, request, jsonify
from db import get_hhp_connection

checkHhpInitialTiming_bp = Blueprint('checkHhpInitialTiming', __name__)

@checkHhpInitialTiming_bp.route('/checkHhpInitialTiming', methods=['POST'])
def checkHhpInitialTiming():
    data = request.get_json(silent=True) or request.form.to_dict()

    section_id = data.get("sectionId") or data.get("section_id")
    loco_id = data.get("locoId") or data.get("loco_id")

    if not section_id or not loco_id:
        return jsonify({
            "error": "Missing required parameters",
            "received": data
        })

    conn = None
    try:
        conn = get_hhp_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        cursor.execute("SELECT * FROM initial_time WHERE loco_id = %s AND section_id = %s", (loco_id, section_id))
        row = cursor.fetchone()

        if row:
            init_time = row['initial_time']
            time_str = init_time.strftime('%Y-%m-%d %H:%M:%S') if hasattr(init_time, 'strftime') else str(init_time)
            return jsonify({
                "message": "✅ Already exists",
                "locoId": row['loco_id'],
                "sectionId": row['section_id'],
                "initial_time": time_str
            })
        else:
            current_time = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO initial_time (loco_id, section_id, initial_time) VALUES (%s, %s, %s)",
                (loco_id, section_id, current_time)
            )
            return jsonify({
                "message": "✅ Inserted new record",
                "locoId": loco_id,
                "sectionId": section_id,
                "initial_time": current_time
            })
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"})
    finally:
        if conn and conn.is_connected():
            conn.close()
