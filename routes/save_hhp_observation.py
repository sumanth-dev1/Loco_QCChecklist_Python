import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify
from db import get_hhp_connection

save_hhp_observation_bp = Blueprint('save_hhp_observation', __name__)

TABLE_MAPPING = {
    1: "document_verification_table",
    2: "verify_serial_numbers_of_equipment_as_per_ic",
    3: "loco_kavach",
    4: "emi_filter_box",
    5: "rib_cab_input_box",
    6: "dmi_lp_ocip",
    7: "rfid_ps_unit",
    8: "loco_antenna_and_gps_gsm_antenna",
    9: "pneumatic_fittings_and_ep_valve_cocks_fixing",
    10: "pressure_sensors_installation_in_loco",
    11: "iru_faviely_units_fixing_for_e70_type_loco",
    12: "psjb_tpm_units_fixing_for_ccb_type_loco",
    13: "sifa_valve_fixing_for_ccb_type_loco",
    14: "pgs_and_speedo_meter_units_fixing",
    15: "rfid_reader_assembly",
    16: "earthing",
    17: "radio_power"
}

@save_hhp_observation_bp.route('/save_hhp_observation', methods=['POST'])
def save_hhp_observation():
    required = ['S_no', 'observation_text', 'observation_status', 'remarks', 'section_id', 'loco_id']
    for field in required:
        val = request.form.get(field)
        if val is None or (val == '' and val != '0'):
            return jsonify({"success": False, "message": f"Missing: {field}"})

    s_no = request.form.get('S_no')
    observation_text = request.form.get('observation_text')
    observation_status = request.form.get('observation_status')
    remarks = request.form.get('remarks')
    try:
        section_id = int(request.form.get('section_id'))
        loco_id = (request.form.get('loco_id') or '').strip()
        if not loco_id:
            raise ValueError("loco_id is empty")
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid section_id or loco_id"})

    barcode = request.form.get('barcode') or request.form.get('barcode_kavach_main_unit')

    if section_id not in TABLE_MAPPING:
        return jsonify({"success": False, "message": "Invalid section ID"})

    table_name = TABLE_MAPPING[section_id]
    image_path = ""

    if 'image' in request.files:
        img_file = request.files['image']
        if img_file and img_file.filename:
            upload_dir = os.path.join('uploads')
            os.makedirs(upload_dir, exist_ok=True)
            filename = f"{int(time.time())}_{secure_filename(img_file.filename)}"
            target_path = os.path.join(upload_dir, filename)
            img_file.save(target_path)
            image_path = f"uploads/{filename}"

    conn = None
    try:
        conn = get_hhp_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        cursor.execute(f"SELECT COUNT(*) AS cnt FROM `{table_name}` WHERE S_no = %s AND loco_id = %s", (s_no, loco_id))
        res = cursor.fetchone()
        exists = (res['cnt'] > 0) if res else False

        if exists:
            if table_name == 'verify_serial_numbers_of_equipment_as_per_ic' and barcode is not None:
                if image_path:
                    sql = f"UPDATE `{table_name}` SET observation_text = %s, observation_status = %s, remarks = %s, barcode = %s, image_path = %s, updated_at = NOW() WHERE S_no = %s AND loco_id = %s"
                    cursor.execute(sql, (observation_text, observation_status, remarks, barcode, image_path, s_no, loco_id))
                else:
                    sql = f"UPDATE `{table_name}` SET observation_text = %s, observation_status = %s, remarks = %s, barcode = %s, updated_at = NOW() WHERE S_no = %s AND loco_id = %s"
                    cursor.execute(sql, (observation_text, observation_status, remarks, barcode, s_no, loco_id))
            else:
                if image_path:
                    sql = f"UPDATE `{table_name}` SET observation_text = %s, observation_status = %s, remarks = %s, image_path = %s, updated_at = NOW() WHERE S_no = %s AND loco_id = %s"
                    cursor.execute(sql, (observation_text, observation_status, remarks, image_path, s_no, loco_id))
                else:
                    sql = f"UPDATE `{table_name}` SET observation_text = %s, observation_status = %s, remarks = %s, updated_at = NOW() WHERE S_no = %s AND loco_id = %s"
                    cursor.execute(sql, (observation_text, observation_status, remarks, s_no, loco_id))
        else:
            if table_name == 'verify_serial_numbers_of_equipment_as_per_ic' and barcode is not None:
                sql = f"INSERT INTO `{table_name}` (S_no, loco_id, observation_text, observation_status, remarks, image_path, barcode, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"
                cursor.execute(sql, (s_no, loco_id, observation_text, observation_status, remarks, image_path, barcode))
            else:
                sql = f"INSERT INTO `{table_name}` (S_no, loco_id, observation_text, observation_status, remarks, image_path, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())"
                cursor.execute(sql, (s_no, loco_id, observation_text, observation_status, remarks, image_path))

        return jsonify({"success": True, "message": "Updated" if exists else "Inserted"})
    except Exception as e:
        return jsonify({"success": False, "message": f"DB Error: {e}"})
    finally:
        if conn and conn.is_connected():
            conn.close()
