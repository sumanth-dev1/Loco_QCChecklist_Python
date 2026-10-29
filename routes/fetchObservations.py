import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify
from db import get_connection

fetchObservations_bp = Blueprint('fetchObservations', __name__)

@fetchObservations_bp.route('/fetchObservations', methods=['GET'])
def fetchObservations():
    loco_id = request.args.get('loco_id')
    if not loco_id:
        return jsonify({'success': False, 'message': 'Invalid request.'})

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        observations = []
        from section_map import SECTION_TABLES
        for i, table_name in SECTION_TABLES.items():
            try:
                cursor.execute(f"SELECT * FROM {table_name} WHERE loco_id = %s", (loco_id,))
                data = cursor.fetchall()
                if data:
                    observations.extend(data)
            except Exception:
                pass

        if observations:
            return jsonify({'success': True, 'observations': observations})
        else:
            return jsonify({'success': False, 'message': 'No observations found.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
