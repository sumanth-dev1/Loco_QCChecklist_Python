import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json, re
from flask import Blueprint, request, jsonify
from db import get_hhp_connection

updateHhpObservations_bp = Blueprint('updateHhpObservations', __name__)

TABLE_NAMES = [
    'document_verification_table',
    'verify_serial_numbers_of_equipment_as_per_ic',
    'loco_kavach',
    'emi_filter_box',
    'rib_cab_input_box',
    'dmi_lp_ocip',
    'rfid_ps_unit',
    'loco_antenna_and_gps_gsm_antenna',
    'pneumatic_fittings_and_ep_valve_cocks_fixing',
    'pressure_sensors_installation_in_loco',
    'iru_faviely_units_fixing_for_e70_type_loco',
    'psjb_tpm_units_fixing_for_ccb_type_loco',
    'sifa_valve_fixing_for_ccb_type_loco',
    'pgs_and_speedo_meter_units_fixing',
    'rfid_reader_assembly',
    'earthing',
    'radio_power'
]

@updateHhpObservations_bp.route('/updateHhpObservations', methods=['POST'])
def updateHhpObservations():
    section_index_raw = request.form.get('section_index')
    section_id_raw = request.form.get('section-id') or request.form.get('section_id') or ''

    sec_idx = None
    if section_index_raw is not None:
        try:
            sec_idx = int(section_index_raw)
        except ValueError:
            pass

    if sec_idx is None and section_id_raw:
        try:
            raw_num = str(section_id_raw).replace('.0', '').replace('_0', '').split('_')[0].split('.')[0]
            sec_idx = int(raw_num) - 1
        except (ValueError, TypeError):
            pass

    if sec_idx is None or sec_idx < 0 or sec_idx >= len(TABLE_NAMES):
        return jsonify({'success': False, 'message': 'Invalid or missing section index.'})

    table_name = TABLE_NAMES[sec_idx]

    loco_id = (request.form.get('loco-id') or request.form.get('loco_id') or '').strip()
    section_id = (request.form.get('section-id') or request.form.get('section_id') or '').strip()
    loco_type = (request.form.get('loco-type') or request.form.get('loco_type') or '').strip()
    brake_type = (request.form.get('brake-type') or request.form.get('brake_type') or '').strip()
    railway_division = (request.form.get('railway-division') or request.form.get('railway_division') or '').strip()
    shed_name = (request.form.get('shed-name') or request.form.get('shed_name') or '').strip()
    inspection_date = (request.form.get('inspection-date') or request.form.get('inspection_date') or '').strip()
    observations_json = request.form.get('observations') or ''

    if not loco_id or not section_id or not observations_json:
        return jsonify({'success': False, 'message': 'Missing required data.'})

    try:
        observations = json.loads(observations_json)
        if not isinstance(observations, list):
            raise ValueError()
    except Exception:
        return jsonify({'success': False, 'message': 'Invalid observations format.'})

    conn = None
    debug_info = []

    try:
        conn = get_hhp_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        for obs in observations:
            s_no = str(obs.get('S_no', '')).strip()
            remarks = obs.get('remarks', '')
            status = obs.get('observation_status', '')
            new_barcode = str(obs.get('barcode', '')).strip() if obs.get('barcode') is not None else ''
            new_height = str(obs.get('height', '')).strip() if obs.get('height') is not None else ''
            client_obs_text = str(obs.get('observation_text', '')).strip()
            image_paths = obs.get('image_paths') or []

            # Check existing observation
            check_sql = f"SELECT observation_text FROM `{table_name}` WHERE loco_id = %s AND (section_id = %s OR section_id = REPLACE(%s, '_', '.')) AND s_no = %s"
            cursor.execute(check_sql, (loco_id, section_id, section_id, s_no))
            existing = cursor.fetchone()

            debug_entry = {
                'S_no': s_no,
                'newBarcode_input': new_barcode,
                'newHeight_input': new_height,
                'clientObservationText': client_obs_text,
                'action': '',
                'existing_observation_text': ''
            }

            if existing:
                existing_text = (existing.get('observation_text') or '').strip()
                debug_entry['existing_observation_text'] = existing_text
                updated_desc = client_obs_text if client_obs_text != '' else existing_text

                if table_name == 'loco_antenna_and_gps_gsm_antenna' and s_no in ['8.1', '8.2', '8.3', '8.4', '8.5', '8.6']:
                    updated_desc = updated_desc.replace('≤', '<=').replace('&lt;=', '<=')
                    updated_desc = re.sub(r'(height shall be\s*<=\s*\d+(?:mm)?\.?)[\s\.\d-]*$', r'\1', updated_desc, flags=re.I)
                    if updated_desc and not updated_desc.endswith('.'):
                        updated_desc += '.'

                    observation_text = updated_desc.strip()
                    if new_height != '':
                        if '(height:' not in status.lower():
                            status = f"{status.strip()} (Height: {new_height})"
                        else:
                            status = re.sub(r'\(Height:.*?\)', f'(Height: {new_height})', status, flags=re.I)
                    else:
                        status = re.sub(r'\s*\(Height:.*?\)', '', status, flags=re.I)
                else:
                    observation_text = updated_desc

                if table_name == 'verify_serial_numbers_of_equipment_as_per_ic':
                    upd_sql = f"""UPDATE `{table_name}` 
                                  SET loco_type = %s, brake_type = %s, railway_division = %s, shed_name = %s, inspection_date = %s, observation_text = %s, barcode = %s, observation_status = %s, remarks = %s, updated_at = NOW() 
                                  WHERE loco_id = %s AND (section_id = %s OR section_id = REPLACE(%s, '_', '.')) AND s_no = %s"""
                    cursor.execute(upd_sql, (loco_type, brake_type, railway_division, shed_name, inspection_date, observation_text, new_barcode, status, remarks, loco_id, section_id, section_id, s_no))
                else:
                    upd_sql = f"""UPDATE `{table_name}` 
                                  SET loco_type = %s, brake_type = %s, railway_division = %s, shed_name = %s, inspection_date = %s, observation_text = %s, observation_status = %s, remarks = %s, updated_at = NOW() 
                                  WHERE loco_id = %s AND (section_id = %s OR section_id = REPLACE(%s, '_', '.')) AND s_no = %s"""
                    cursor.execute(upd_sql, (loco_type, brake_type, railway_division, shed_name, inspection_date, observation_text, status, remarks, loco_id, section_id, section_id, s_no))

                debug_entry['action'] = 'updated'

                if isinstance(image_paths, list) and image_paths:
                    del_img = "DELETE FROM images WHERE loco_id = %s AND s_no = %s"
                    cursor.execute(del_img, (loco_id, s_no))
                    ins_img = "INSERT INTO images (entity_type, loco_id, s_no, image_path, created_at) VALUES (%s, %s, %s, %s, NOW())"
                    for img_p in image_paths:
                        cursor.execute(ins_img, ('hhp_section', loco_id, s_no, img_p))

            else:
                # Insert
                if table_name == 'verify_serial_numbers_of_equipment_as_per_ic':
                    ins_sql = f"""INSERT INTO `{table_name}` 
                                  (loco_id, section_id, s_no, loco_type, brake_type, railway_division, shed_name, inspection_date, observation_text, barcode, observation_status, remarks, created_at, updated_at) 
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"""
                    cursor.execute(ins_sql, (loco_id, section_id, s_no, loco_type, brake_type, railway_division, shed_name, inspection_date, client_obs_text, new_barcode, status, remarks))
                else:
                    insert_text = client_obs_text
                    if table_name == 'loco_antenna_and_gps_gsm_antenna' and s_no in ['8.1', '8.2', '8.3', '8.4', '8.5', '8.6']:
                        insert_text = insert_text.replace('≤', '<=').replace('&lt;=', '<=')
                        if insert_text and not insert_text.endswith('.'):
                            insert_text += '.'
                        if new_height != '':
                            insert_text = re.sub(r'\s*(\d+)?$', '', insert_text).strip() + ' ' + new_height

                    if not insert_text:
                        insert_text = new_height if new_height != '' else ''

                    ins_sql = f"""INSERT INTO `{table_name}` 
                                  (loco_id, section_id, s_no, loco_type, brake_type, railway_division, shed_name, inspection_date, observation_text, observation_status, remarks, created_at, updated_at) 
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"""
                    cursor.execute(ins_sql, (loco_id, section_id, s_no, loco_type, brake_type, railway_division, shed_name, inspection_date, insert_text, status, remarks))

                debug_entry['action'] = 'inserted'
                debug_entry['finalHeight'] = new_height

                if isinstance(image_paths, list) and image_paths:
                    ins_img = "INSERT INTO images (entity_type, loco_id, s_no, image_path, created_at) VALUES (%s, %s, %s, %s, NOW())"
                    for img_p in image_paths:
                        cursor.execute(ins_img, ('hhp_section', loco_id, s_no, img_p))

            debug_info.append(debug_entry)

        return jsonify({'success': True, 'message': 'Observations and images updated successfully.', 'debug': debug_info})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating observations: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
