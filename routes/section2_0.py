import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json, datetime, html, re, zoneinfo
from flask import Blueprint, request, jsonify
from db import get_connection

section2_0_bp = Blueprint('section2_0', __name__)

def format_observations(label, values):
    value_array = re.split(r'\s+', str(values).strip())
    formatted_values = []
    for idx, val in enumerate(value_array):
        formatted_values.append(f"{label} {idx + 1}: {val}")
    return ", ".join(formatted_values)

@section2_0_bp.route('/section2_0', methods=['POST'])
def section2_0():
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

        formatted_observations = []

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)

            cursor.execute("SELECT * FROM initial_time WHERE loco_id=%s AND section_id=%s", (loco_id, section_id))
            row = cursor.fetchone()
            if row and row.get('initial_time'):
                created_at = str(row['initial_time'])
            else:
                created_at = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("DELETE FROM verify_serial_numbers_of_equipment_as_per_ic WHERE loco_id = %s AND (section_id = %s OR section_id = %s)", (loco_id, section_id, str(section_id).replace('.0', '')))
            sql = """INSERT INTO verify_serial_numbers_of_equipment_as_per_ic (
                loco_id, loco_type, brake_type, railway_division, shed_name,
                inspection_date, observation_text, remarks, barcode, S_no,
                observation_status, section_id, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())"""

            for obs in observations:
                barcode = obs.get('barcode_kavach_main_unit')
                cursor.execute(sql, (
                    loco_id, loco_type, brake_type, railway_division, shed_name, inspection_date,
                    html.escape(str(obs.get('observation_text', ''))),
                    html.escape(str(obs.get('remarks', ''))),
                    barcode,
                    html.escape(str(obs.get('S_no', ''))),
                    html.escape(str(obs.get('observation_status', ''))),
                    section_id,
                    created_at
                ))

                formatted_observations.append(format_observations(obs.get('observation_text', ''), obs.get('S_no', '')))

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

            return jsonify({
                'success': True,
                'message': 'Observations and images saved successfully.',
                'formattedObservations': formatted_observations,
                'sectionId': section_id,
                'locoId': loco_id
            })
        except Exception as e:
            return jsonify({'success': False, 'message': f'Server error: {e}'})
        finally:
            if conn and conn.is_connected():
                conn.close()
    return jsonify({'success': False, 'message': 'Missing fields'})
