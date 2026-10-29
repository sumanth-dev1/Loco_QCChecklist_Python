import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json, datetime, html
from flask import Blueprint, request, jsonify
from db import get_connection

section1_0_bp = Blueprint('section1_0', __name__)

@section1_0_bp.route('/section1_0', methods=['POST'])
def section1_0():
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
            return jsonify({'success': False, 'message': 'Missing necessary POST data'})

        locoID = html.escape(loco_id)
        sectionID = html.escape(section_id)
        locoType = html.escape(loco_type)
        brakeType = html.escape(brake_type)
        railwayDivision = html.escape(railway_division)
        shedName = html.escape(shed_name)
        inspectionDate = html.escape(inspection_date)

        try:
            observations = json.loads(observations_raw)
        except Exception:
            return jsonify({'success': False, 'message': 'Error: Invalid JSON format for observations.'})

        if not observations or not isinstance(observations, list):
            return jsonify({'success': False, 'message': 'Error: No observations to save.'})

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)

            cursor.execute("SELECT * FROM initial_time WHERE loco_id=%s AND section_id=%s", (locoID, sectionID))
            row = cursor.fetchone()
            if row and row.get('initial_time'):
                created_at = str(row['initial_time'])
            else:
                created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            sql = """INSERT INTO document_verification_table 
(loco_id, loco_type, brake_type, railway_division, shed_name, inspection_date, observation_text, remarks, S_no, image_path, observation_status, section_id, created_at, updated_at) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, ''), %s, %s, %s, NOW())"""

            for obs in observations:
                image_path = html.escape(obs['image_path']) if obs.get('image_path') else None
                cursor.execute(sql, (
                    locoID, locoType, brakeType, railwayDivision, shedName, inspectionDate,
                    html.escape(str(obs.get('observation_text', ''))),
                    html.escape(str(obs.get('remarks', ''))),
                    html.escape(str(obs.get('S_no', ''))),
                    image_path,
                    html.escape(str(obs.get('observation_status', ''))),
                    sectionID,
                    created_at
                ))

            return jsonify({
                'success': True,
                'message': 'Observations and images saved successfully.',
                'console_log': f"<script>console.log('Observations:', {json.dumps(observations)});</script>"
            })
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error saving observations: {e}'})
        finally:
            if conn and conn.is_connected():
                conn.close()
    return jsonify({'success': False, 'message': 'Missing necessary POST data'})
