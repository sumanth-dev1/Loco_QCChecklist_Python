import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime, zoneinfo
from flask import Blueprint, request, jsonify
from db import get_connection

checkInitialTiming_bp = Blueprint('checkInitialTiming', __name__)

@checkInitialTiming_bp.route('/checkInitialTiming', methods=['POST'])
def checkInitialTiming():
    data = request.get_json(silent=True) or {}
    loco_id = data.get('locoId')
    section_id = data.get('sectionId')

    if not loco_id or not section_id:
        return jsonify({"error": "Missing required parameters", "received": data})

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM initial_time WHERE loco_id = %s AND section_id = %s", (loco_id, str(section_id)))
        row = cursor.fetchone()

        if row:
            return jsonify({
                "message": "✅ Already exists",
                "locoId": row['loco_id'],
                "sectionId": row['section_id'],
                "initial_time": str(row['initial_time'])
            })
        else:
            current_time = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO initial_time (loco_id, section_id, initial_time) VALUES (%s, %s, %s)",
                (loco_id, str(section_id), current_time)
            )
            return jsonify({
                "message": "✅ Inserted new record",
                "locoId": loco_id,
                "sectionId": section_id,
                "initial_time": current_time
            })
    except Exception as e:
        return jsonify({"error": f"Insert failed: {e}"})
    finally:
        if conn and conn.is_connected():
            conn.close()
