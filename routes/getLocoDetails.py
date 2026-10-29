import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, jsonify
from db import get_connection

getLocoDetails_bp = Blueprint('getLocoDetails', __name__)

@getLocoDetails_bp.route('/getLocoDetails', methods=['GET', 'POST'])
def getLocoDetails():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM loco LIMIT 1")
        row = cursor.fetchone()

        if row:
            if row.get('inspection_Date'):
                row['inspection_Date'] = str(row['inspection_Date'])
            if row.get('start_time'):
                row['start_time'] = str(row['start_time'])
            if row.get('completed_time'):
                row['completed_time'] = str(row['completed_time'])

            return jsonify({"success": True, "locoDetails": row})
        else:
            return jsonify({"success": False, "message": "No loco details found"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Connection failed: {e}"})
    finally:
        if conn and conn.is_connected():
            conn.close()
