import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime, zoneinfo
from flask import Blueprint, request, jsonify
from db import get_hhp_connection

connect_hhp_bp = Blueprint('connect_hhp', __name__)

@connect_hhp_bp.route('/connect_hhp', methods=['POST'])
def connect_hhp():
    if request.method != 'POST':
        return jsonify({'success': False, 'message': '❌ Only POST allowed'})

    loco_id = (request.form.get('loco-id') or '').strip()
    loco_type = (request.form.get('loco-type') or '').strip()
    brake_type = (request.form.get('brake-type') or '').strip()
    railway_division = (request.form.get('railway-division') or '').strip()
    shed_name = (request.form.get('shed-name') or '').strip()
    inspection_date = (request.form.get('inspection-date') or '').strip()

    if not loco_id or not loco_type or not brake_type or not railway_division or not shed_name or not inspection_date:
        return jsonify({'success': False, 'message': '❌ All fields are required'})

    current_time = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')

    conn = None
    try:
        conn = get_hhp_connection()
        cursor = conn.cursor(buffered=True)

        cursor.execute("SELECT 1 FROM loco WHERE Loco_Id = %s", (loco_id,))
        row = cursor.fetchone()

        if row:
            return jsonify({'success': True, 'message': 'ℹ️ HHP Loco already exists. Start time preserved.'})
        else:
            cursor.execute(
                """INSERT INTO loco 
                (Loco_Id, Loco_type, Brake_type, Railway_Division, Shed_name, inspection_Date, start_time, completed_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (loco_id, loco_type, brake_type, railway_division, shed_name, inspection_date, current_time, current_time)
            )
            return jsonify({'success': True, 'message': '✅ HHP Loco info saved with start time'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Insert failed: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
