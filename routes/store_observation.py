import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json, html, os, uuid
from flask import Blueprint, request, jsonify
from db import get_connection

store_observation_bp = Blueprint('store_observation', __name__)

@store_observation_bp.route('/store_observation', methods=['POST'])
def store_observation():
    if request.method == 'POST':
        loco_id = request.form.get('loco-id')
        section_id = request.form.get('section-id')
        observations_raw = request.form.get('observations')
        loco_type = request.form.get('loco-type')
        brake_type = request.form.get('brake-type')
        railway_division = request.form.get('railway-division')
        shed_name = request.form.get('shed-name')

        if not all([loco_id, section_id, observations_raw, loco_type, brake_type, railway_division, shed_name]):
            return jsonify({'success': False, 'message': 'Missing necessary POST data'})

        locoID = html.escape(loco_id)
        sectionID = html.escape(section_id)
        locoType = html.escape(loco_type)
        brakeType = html.escape(brake_type)
        railwayDivision = html.escape(railway_division)
        shedName = html.escape(shed_name)

        try:
            observations = json.loads(observations_raw)
        except Exception:
            return jsonify({'success': False, 'message': 'Error: Invalid JSON format for observations.'})

        if not observations or not isinstance(observations, list):
            return jsonify({'success': False, 'message': 'Error: No observations to save.'})

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(buffered=True)

            cursor.execute("SELECT COUNT(*) FROM observations WHERE loco_id = %s AND section_id = %s", (locoID, sectionID))
            count = cursor.fetchone()[0]

            if count > 0:
                return jsonify({'success': False, 'message': 'Details already filled for this loco ID and section.'})

            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    upload_dir = 'uploads/'
                    os.makedirs(upload_dir, exist_ok=True)
                    ext = file.filename.rsplit('.', 1)[-1] if '.' in file.filename else 'jpg'
                    filename = f"file-{uuid.uuid4().hex}.{ext}"
                    target_path = os.path.join(upload_dir, filename)
                    file.save(target_path)
                    image_path = target_path.replace('\\', '/')

            sql = """INSERT INTO observations 
                     (loco_id, section_id, loco_type, brake_type, railway_division, shed_name, observation_text, remarks, S_no, image_path, observation_status) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            for obs in observations:
                obs_text = html.escape(str(obs.get('observation_text', '')))
                remarks = html.escape(str(obs.get('remarks', ''))) if 'remarks' in obs else ''
                sno = html.escape(str(obs.get('S_no', '')))

                obs_status = str(obs.get('observation_status', '')).strip().lower()
                if obs_status == 'please choose an option':
                    continue

                if obs_status == 'ok':
                    status_val = 'Available'
                elif obs_status == 'not-ok':
                    status_val = 'NOT Available'
                else:
                    return jsonify({'success': False, 'message': 'Error: Invalid observation status.'})

                cursor.execute(sql, (
                    locoID, sectionID, locoType, brakeType, railwayDivision, shedName,
                    obs_text, remarks, sno, image_path, status_val
                ))

            return jsonify({'success': True, 'message': 'Observations saved successfully.'})
        except Exception:
            return jsonify({'success': False, 'message': 'Error saving observations.'})
        finally:
            if conn and conn.is_connected():
                conn.close()

    return jsonify({'success': False, 'message': 'Missing necessary POST data'})
