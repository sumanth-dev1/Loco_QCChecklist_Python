import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json, os
from flask import Blueprint, request, jsonify
from db import get_connection

observation_bp = Blueprint('observation', __name__)

@observation_bp.route('/observation', methods=['POST'])
def observation():
    if request.method == 'POST':
        loco_id = request.form.get('loco-id')
        section_id = request.form.get('section-id')
        observations_raw = request.form.get('observations')
        loco_type = request.form.get('loco-type')
        brake_type = request.form.get('brake-type')
        railway_division = request.form.get('railway-division')
        shed_name = request.form.get('shed-name')

        if loco_id and section_id and observations_raw and loco_type and brake_type and railway_division and shed_name:
            try:
                observations = json.loads(observations_raw)
            except Exception:
                return jsonify({"error": "Invalid observations JSON"})

            conn = None
            try:
                conn = get_connection()
                cursor = conn.cursor(buffered=True)

                sql = """INSERT INTO observations 
                         (loco_id, section_id, loco_type, brake_type, railway_division, shed_name, observation_text, remarks, S_no, image_path, observation_status) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

                for idx, obs in enumerate(observations):
                    obs_text = obs.get('observation_text', '')
                    remarks = obs.get('remarks', '')
                    sno = obs.get('S_no', '')
                    obs_status = obs.get('observation_status', '')
                    image_path = ''

                    if 'image' in request.files:
                        file = request.files['image']
                        if file and file.filename != '':
                            upload_dir = 'uploads/'
                            os.makedirs(upload_dir, exist_ok=True)
                            ext = file.filename.rsplit('.', 1)[-1] if '.' in file.filename else 'jpg'
                            new_name = f"file-{idx + 1}.{ext}"
                            full_path = os.path.join(upload_dir, new_name)
                            file.save(full_path)
                            image_path = full_path.replace('\\', '/')
                    elif obs.get('image_path') and str(obs.get('image_path')).startswith('data:image/jpeg;base64,'):
                        import base64
                        img_data = str(obs.get('image_path')).replace('data:image/jpeg;base64,', '')
                        decoded = base64.b64decode(img_data)
                        upload_dir = 'uploads/'
                        os.makedirs(upload_dir, exist_ok=True)
                        new_name = f"file-{idx + 1}.jpg"
                        full_path = os.path.join(upload_dir, new_name)
                        with open(full_path, 'wb') as f:
                            f.write(decoded)
                        image_path = full_path.replace('\\', '/')

                    cursor.execute(sql, (
                        loco_id, section_id, loco_type, brake_type, railway_division, shed_name,
                        obs_text, remarks, sno, image_path, obs_status
                    ))

                return jsonify({"success": "Observations added successfully."})
            except Exception as e:
                return jsonify({"error": str(e)})
            finally:
                if conn and conn.is_connected():
                    conn.close()

        elif loco_id:
            sno = request.form.get('S_no')
            conn = None
            try:
                conn = get_connection()
                cursor = conn.cursor(dictionary=True, buffered=True)

                if sno:
                    cursor.execute("SELECT * FROM observations WHERE loco_id = %s AND S_no = %s", (loco_id, sno))
                else:
                    cursor.execute("SELECT * FROM observations WHERE loco_id = %s", (loco_id,))

                rows = cursor.fetchall()
                return jsonify(rows)
            except Exception as e:
                return jsonify({"error": str(e)})
            finally:
                if conn and conn.is_connected():
                    conn.close()
        else:
            return jsonify({"error": "Required parameters not provided."})
    return jsonify({"error": "Required parameters not provided."})
