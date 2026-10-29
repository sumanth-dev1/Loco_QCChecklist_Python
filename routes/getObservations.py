import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import html
from flask import Blueprint, request, jsonify
from db import get_connection

getObservations_bp = Blueprint('getObservations', __name__)

@getObservations_bp.route('/getObservations', methods=['GET', 'POST'])
def getObservations():
    loco_id_raw = (
        request.form.get('loco-id') or
        request.form.get('loco_id') or
        request.args.get('loco-id') or
        request.args.get('loco_id')
    )
    if not loco_id_raw:
        return jsonify({'success': False, 'message': 'Loco ID is missing.'})

    locoID = html.escape(str(loco_id_raw).strip())

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        cursor.execute("SELECT Loco_Id as loco_id, Loco_type as loco_type, Brake_type as brake_type, Railway_Division as railway_division, Shed_name as shed_name FROM loco WHERE Loco_Id = %s LIMIT 1", (locoID,))
        locoDetails = cursor.fetchone()

        observations = []
        from section_map import SECTION_TABLES
        for sec_num, table_name in SECTION_TABLES.items():
            try:
                cursor.execute(f"SELECT S_no, observation_text, remarks, observation_status, section_id FROM {table_name} WHERE loco_id = %s", (locoID,))
                obs_rows = cursor.fetchall()
                if obs_rows:
                    observations.extend(obs_rows)
            except Exception:
                pass

        if locoDetails or observations:
            return jsonify({'success': True, 'locoDetails': locoDetails, 'observations': observations})
        else:
            return jsonify({'success': False, 'message': 'No data found for this loco ID.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
