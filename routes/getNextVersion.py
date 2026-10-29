import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify
from db import get_connection

getNextVersion_bp = Blueprint('getNextVersion', __name__)

@getNextVersion_bp.route('/getNextVersion', methods=['GET'])
def getNextVersion():
    loco_id = (request.args.get('loco_id') or '').strip()
    if not loco_id:
        return jsonify({'success': False, 'message': 'Loco ID is required'})

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT latest_version FROM report_versions WHERE loco_id = %s", (loco_id,))
        row = cursor.fetchone()

        if row:
            next_version = int(row['latest_version']) + 1
            cursor.execute("UPDATE report_versions SET latest_version = %s WHERE loco_id = %s", (next_version, loco_id))
        else:
            next_version = 1
            cursor.execute("INSERT INTO report_versions (loco_id, latest_version) VALUES (%s, %s)", (loco_id, next_version))

        return jsonify({'success': True, 'version': next_version})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
