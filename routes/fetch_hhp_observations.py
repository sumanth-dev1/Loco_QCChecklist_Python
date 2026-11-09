import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify
from db import get_hhp_connection

fetch_hhp_observations_bp = Blueprint('fetch_hhp_observations', __name__)

TABLE_NAMES = [
    "document_verification_table", "verify_serial_numbers_of_equipment_as_per_ic", "loco_kavach",
    "emi_filter_box", "rib_cab_input_box", "dmi_lp_ocip", "rfid_ps_unit",
    "loco_antenna_and_gps_gsm_antenna", "pneumatic_fittings_and_ep_valve_cocks_fixing",
    "pressure_sensors_installation_in_loco", "iru_faviely_units_fixing_for_e70_type_loco",
    "psjb_tpm_units_fixing_for_ccb_type_loco", "sifa_valve_fixing_for_ccb_type_loco",
    "pgs_and_speedo_meter_units_fixing", "rfid_reader_assembly", "earthing", "radio_power"
]

@fetch_hhp_observations_bp.route('/fetch_hhp_observations', methods=['GET'])
def fetch_hhp_observations():
    loco_id = request.args.get('loco_id')
    if not loco_id:
        return jsonify({'status': 'error', 'message': 'Missing loco_id'})

    conn = None
    try:
        conn = get_hhp_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        observations = []

        try:
            cursor.execute("SHOW COLUMNS FROM `verify_serial_numbers_of_equipment_as_per_ic` LIKE 'atr_serial'")
            has_atr_col = bool(cursor.fetchone())
        except Exception:
            has_atr_col = False
        atr_col_expr = ", atr_serial" if has_atr_col else ", NULL as atr_serial"

        for table_name in TABLE_NAMES:
            barcode_select = f", barcode {atr_col_expr}" if table_name == "verify_serial_numbers_of_equipment_as_per_ic" else ", NULL as barcode, NULL as atr_serial"
            sql = f"SELECT S_no, observation_text, observation_status, remarks, image_path, created_at, updated_at {barcode_select} FROM `{table_name}` WHERE loco_id = %s"
            cursor.execute(sql, (loco_id,))
            rows = cursor.fetchall()

            for row in rows:
                s_no = str(row['S_no'])
                img_cursor = conn.cursor(dictionary=True, buffered=True)
                img_cursor.execute("SELECT image_path FROM images WHERE loco_id = %s AND s_no = %s", (loco_id, s_no))
                img_rows = img_cursor.fetchall()
                image_paths = [img_row['image_path'] for img_row in img_rows if img_row.get('image_path')]
                img_cursor.close()

                if not image_paths and row.get('image_path'):
                    image_paths = [p.strip() for p in str(row['image_path']).split(',') if p.strip()]

                observations.append({
                    'S_no': row['S_no'],
                    'observation_text': row['observation_text'],
                    'observation_status': row['observation_status'],
                    'remarks': row['remarks'],
                    'image_paths': image_paths,
                    'barcode': row.get('barcode'),
                    'atr_serial': row.get('atr_serial'),
                    'created_at': str(row['created_at']) if row.get('created_at') else None,
                    'updated_at': str(row['updated_at']) if row.get('updated_at') else None
                })

        # Deduplicate observations by S_no to guarantee no section repeats
        dedup_observations = {}
        for obs in observations:
            sno = str(obs.get('S_no') or '').strip()
            if not sno:
                continue
            if sno not in dedup_observations:
                dedup_observations[sno] = obs
            else:
                existing_stat = str(dedup_observations[sno].get('observation_status') or '').strip()
                curr_stat = str(obs.get('observation_status') or '').strip()
                if curr_stat and not existing_stat:
                    dedup_observations[sno] = obs
                elif curr_stat:
                    dedup_observations[sno] = obs
        observations = list(dedup_observations.values())

        if observations:
            return jsonify({'status': 'success', 'data': observations})
        else:
            return jsonify({'status': 'error', 'message': 'No observations found'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'DB error: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
