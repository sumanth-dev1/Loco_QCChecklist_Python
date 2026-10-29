import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json, datetime, html
from flask import Blueprint, request, jsonify
from db import get_hhp_connection

hhp_section9_0_bp = Blueprint('hhp_section9_0', __name__)

@hhp_section9_0_bp.route('/hhp_section9_0', methods=['POST'])
def hhp_section9_0():
    if request.method == 'POST':
        loco_id = request.form.get('loco-id')
        section_id = request.form.get('section-id')
        observations_raw = request.form.get('observations')
        loco_type = request.form.get('loco-type') or ''
        brake_type = request.form.get('brake-type') or ''
        railway_division = request.form.get('railway-division') or ''
        shed_name = request.form.get('shed-name') or ''
        inspection_date = request.form.get('inspection-date') or ''

        if loco_id is None or section_id is None or observations_raw is None:
            return jsonify({'success': False, 'message': 'Missing necessary POST data'})

        locoID = html.escape(str(loco_id).strip())
        sectionID = html.escape(str(section_id).strip())
        locoType = html.escape(str(loco_type).strip())
        brakeType = html.escape(str(brake_type).strip())
        railwayDivision = html.escape(str(railway_division).strip())
        shedName = html.escape(str(shed_name).strip())
        inspectionDate = html.escape(str(inspection_date).strip())

        try:
            observations = json.loads(observations_raw)
        except Exception:
            return jsonify({'success': False, 'message': 'Error: Invalid JSON format for observations.'})

        if not observations or not isinstance(observations, list):
            return jsonify({'success': False, 'message': 'Error: No observations to save.'})

        conn = None
        try:
            conn = get_hhp_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)

            # Master loco lookup fallback if locoType, brakeType, or inspectionDate are empty
            if not locoType or not brakeType or not inspectionDate:
                cursor.execute("SELECT Loco_type, Brake_type, inspection_Date FROM loco WHERE Loco_Id = %s", (locoID,))
                master = cursor.fetchone()
                if master:
                    if not locoType:
                        locoType = master.get('Loco_type') or ''
                    if not brakeType:
                        brakeType = master.get('Brake_type') or ''
                    if not inspectionDate and master.get('inspection_Date'):
                        inspectionDate = str(master.get('inspection_Date'))

            cursor.execute("SELECT * FROM initial_time WHERE loco_id=%s AND section_id=%s", (locoID, sectionID))
            row = cursor.fetchone()
            if row and row.get('initial_time'):
                created_at = str(row['initial_time'])
            else:
                created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("DELETE FROM `pneumatic_fittings_and_ep_valve_cocks_fixing` WHERE loco_id = %s", (locoID,))

            sql = """INSERT INTO `pneumatic_fittings_and_ep_valve_cocks_fixing` 
(loco_id, loco_type, brake_type, railway_division, shed_name, inspection_date, observation_text, remarks, S_no, image_path, observation_status, section_id, created_at, updated_at) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, ''), %s, %s, %s, NOW())"""

            for obs in observations:
                image_path = None
                img_paths_arr = []
                if obs.get('image_paths') and isinstance(obs['image_paths'], list):
                    img_paths_arr = [str(p).strip() for p in obs['image_paths'] if str(p).strip()]
                    image_path = ','.join(img_paths_arr)
                elif obs.get('image_path'):
                    image_path = html.escape(str(obs['image_path']))
                    img_paths_arr = [p.strip() for p in image_path.split(',') if p.strip()]

                s_no = html.escape(str(obs.get('S_no', '')))
                if img_paths_arr:
                    cursor.execute("DELETE FROM images WHERE loco_id = %s AND s_no = %s", (locoID, s_no))
                    for img_p in img_paths_arr:
                        cursor.execute("INSERT INTO images (entity_type, loco_id, s_no, image_path, created_at) VALUES (%s, %s, %s, %s, %s)",
                                       ('hhp_section', locoID, s_no, img_p, created_at))

                cursor.execute(sql, (
                    locoID, locoType, brakeType, railwayDivision, shedName, inspectionDate,
                    html.escape(str(obs.get('observation_text', ''))),
                    html.escape(str(obs.get('remarks', ''))),
                    s_no,
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
