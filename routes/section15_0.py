import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json, datetime
from flask import Blueprint, request, jsonify
from db import get_connection

section15_0_bp = Blueprint('section15_0', __name__)

@section15_0_bp.route('/section15_0', methods=['POST'])
def section15_0():
    if request.method == 'POST':
        loco_id = request.form.get('loco-id')
        section_id = request.form.get('section-id')
        observations_raw = request.form.get('observations')
        loco_type = request.form.get('loco-type')
        brake_type = request.form.get('brake-type')
        railway_division = request.form.get('railway-division')
        shed_name = request.form.get('shed-name')
        inspection_date = request.form.get('inspection-date')

        if loco_id is None or section_id is None or observations_raw is None:
            return jsonify({'success': False, 'message': 'Missing fields'})

        try:
            observations = json.loads(observations_raw)
        except Exception:
            return jsonify({'success': False, 'message': 'Invalid observation data'})

        if not observations or not isinstance(observations, list):
            return jsonify({'success': False, 'message': 'Invalid observation data'})

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)

            cursor.execute("SELECT * FROM initial_time WHERE loco_id=%s AND section_id=%s", (loco_id, section_id))
            row = cursor.fetchone()
            if row and row.get('initial_time'):
                created_at = str(row['initial_time'])
            else:
                created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("DELETE FROM rfid_reader_assembly WHERE loco_id = %s AND (section_id = %s OR section_id = %s)", (loco_id, section_id, str(section_id).replace('.0', '')))
            sql = """INSERT INTO rfid_reader_assembly (
                loco_id, loco_type, brake_type, railway_division, shed_name,
                inspection_date, observation_text, remarks, S_no,
                observation_status, section_id, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())"""

            for obs in observations:
                cursor.execute(sql, (
                    loco_id, loco_type, brake_type, railway_division, shed_name, inspection_date,
                    obs.get('observation_text'), obs.get('remarks'), obs.get('S_no'),
                    obs.get('observation_status'), section_id, created_at
                ))

                image_paths = obs.get('image_paths')
                if image_paths and isinstance(image_paths, list):
                    del_stmt = conn.cursor()
                    del_stmt.execute("DELETE FROM images WHERE loco_id = %s AND s_no = %s", (loco_id, obs.get('S_no')))
                    del_stmt.close()

                    for img_path in image_paths:
                        img_stmt = conn.cursor()
                        img_stmt.execute(
                            "INSERT INTO images (entity_type, loco_id, s_no, image_path, created_at) VALUES (%s, %s, %s, %s, %s)",
                            ('radio_power', loco_id, obs.get('S_no'), img_path, created_at)
                        )
                        img_stmt.close()

            return jsonify({'success': True, 'message': 'Observations and images saved.'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Server error: {e}'})
        finally:
            if conn and conn.is_connected():
                conn.close()
    return jsonify({'success': False, 'message': 'Missing fields'})
