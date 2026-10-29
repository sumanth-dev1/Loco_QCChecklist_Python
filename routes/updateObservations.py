import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json, re
from flask import Blueprint, request, jsonify
from db import get_connection

updateObservations_bp = Blueprint('updateObservations', __name__)

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

@updateObservations_bp.route('/updateObservations', methods=['POST'])
def updateObservations():
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

    loco_id = (request.form.get('loco-id') or '').strip()
    section_id = (request.form.get('section-id') or '').strip() or str(section_id_raw)
    loco_type = (request.form.get('loco-type') or '').strip()
    brake_type = (request.form.get('brake-type') or '').strip()
    railway_division = (request.form.get('railway-division') or '').strip()
    shed_name = (request.form.get('shed-name') or '').strip()
    inspection_date = (request.form.get('inspection-date') or '').strip()
    observations_json = request.form.get('observations') or ''

    if not loco_id or not section_id or not observations_json:
        return jsonify({'success': False, 'message': 'Missing required data.'})

    try:
        observations = json.loads(observations_json)
    except Exception:
        return jsonify({'success': False, 'message': 'Invalid observations format.'})

    if not observations or not isinstance(observations, list):
        return jsonify({'success': False, 'message': 'Invalid observations format.'})

    conn = None
    debug_info = []

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        for obs in observations:
            s_no = obs.get('S_no')
            remarks = obs.get('remarks', '')
            status = obs.get('observation_status', '')
            new_barcode = str(obs.get('barcode', '')).strip()
            new_height = str(obs.get('height', '')).strip()
            client_obs_text = str(obs.get('observation_text', '')).strip()
            image_paths = obs.get('image_paths', [])

            cursor.execute(
                f"SELECT observation_text FROM {table_name} WHERE loco_id = %s AND section_id = %s AND s_no = %s",
                (loco_id, section_id, s_no)
            )
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
                existing_text = str(existing['observation_text'] or '').strip()
                debug_entry['existing_observation_text'] = existing_text

                updated_description = client_obs_text if client_obs_text != '' else existing_text

                if table_name == 'loco_antenna_and_gps_gsm_antenna' and s_no in ['8.1', '8.2', '8.3', '8.4', '8.5', '8.6']:
                    updated_description = updated_description.replace('≤', '<=').replace('&lt;=', '<=')
                    updated_description = re.sub(r'(height shall be\s*<=\s*\d+(?:mm)?\.?)[\s\.\d-]*$', r'', updated_description, flags=re.IGNORECASE)
                    if updated_description != '' and not updated_description.endswith('.'):
                        updated_description += '.'

                    observation_text = updated_description.strip()

                    if new_height != '':
                        if '(Height:' not in status.lower():
                            status = f"{status.strip()} (Height: {new_height})"
                        else:
                            status = re.sub(r'\(Height:.*?\)', f'(Height: {new_height})', status, flags=re.IGNORECASE)
                    else:
                        status = re.sub(r'\s*\(Height:.*?\)', '', status, flags=re.IGNORECASE)
                else:
                    m = re.match(r'^(.*):\s*(\d{10,15})$', existing_text)
                    if m:
                        existing_description = m.group(1).strip()
                        existing_barcode = m.group(2).strip()
                    else:
                        existing_description = existing_text
                        existing_barcode = ''

                    if new_barcode == '':
                        new_barcode = existing_barcode

                    if new_barcode != '':
                        if table_name == 'verify_serial_numbers_of_equipment_as_per_ic':
                            observation_text = updated_description.strip()
                        else:
                            base_description = client_obs_text if client_obs_text != '' else existing_description
                            observation_text = f"{base_description.strip()}: {new_barcode}"
                    else:
                        observation_text = updated_description.strip()

                if table_name == 'verify_serial_numbers_of_equipment_as_per_ic':
                    update_sql = f"""UPDATE {table_name}
                        SET loco_type = %s, brake_type = %s, railway_division = %s, shed_name = %s, inspection_date = %s, observation_text = %s, barcode = %s, observation_status = %s, remarks = %s, updated_at = NOW()
                        WHERE loco_id = %s AND section_id = %s AND s_no = %s"""
                    cursor.execute(update_sql, (loco_type, brake_type, railway_division, shed_name, inspection_date, observation_text, new_barcode, status, remarks, loco_id, section_id, s_no))
                else:
                    update_sql = f"""UPDATE {table_name}
                        SET loco_type = %s, brake_type = %s, railway_division = %s, shed_name = %s, inspection_date = %s, observation_text = %s, observation_status = %s, remarks = %s, updated_at = NOW()
                        WHERE loco_id = %s AND section_id = %s AND s_no = %s"""
                    cursor.execute(update_sql, (loco_type, brake_type, railway_division, shed_name, inspection_date, observation_text, status, remarks, loco_id, section_id, s_no))

                debug_entry['action'] = 'updated'

                if image_paths and isinstance(image_paths, list):
                    del_stmt = conn.cursor()
                    del_stmt.execute("DELETE FROM images WHERE loco_id = %s AND s_no = %s", (loco_id, s_no))
                    del_stmt.close()

                    for img_path in image_paths:
                        img_stmt = conn.cursor()
                        img_stmt.execute(
                            "INSERT INTO images (entity_type, loco_id, s_no, image_path, created_at) VALUES (%s, %s, %s, %s, NOW())",
                            ('radio_power', loco_id, s_no, img_path)
                        )
                        img_stmt.close()
            else:
                if table_name == 'verify_serial_numbers_of_equipment_as_per_ic':
                    insert_sql = f"""INSERT INTO {table_name} 
                        (loco_id, section_id, s_no, loco_type, brake_type, railway_division, shed_name, inspection_date, observation_text, barcode, observation_status, remarks, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"""
                    cursor.execute(insert_sql, (loco_id, section_id, s_no, loco_type, brake_type, railway_division, shed_name, inspection_date, client_obs_text.strip(), new_barcode, status, remarks))
                else:
                    insert_sql = f"""INSERT INTO {table_name} 
                        (loco_id, section_id, s_no, loco_type, brake_type, railway_division, shed_name, inspection_date, observation_text, observation_status, remarks, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"""

                    insert_obs_text = client_obs_text.strip()
                    if table_name == 'loco_antenna_and_gps_gsm_antenna' and s_no in ['8.1', '8.2', '8.3', '8.4', '8.5', '8.6']:
                        insert_obs_text = insert_obs_text.replace('≤', '<=').replace('&lt;=', '<=')
                        if insert_obs_text != '' and not insert_obs_text.endswith('.'):
                            insert_obs_text += '.'
                        if new_height != '':
                            insert_obs_text = re.sub(r'\s*(\d+)?$', '', insert_obs_text) + f" {new_height}"
                    if insert_obs_text == '':
                        insert_obs_text = new_height if new_height != '' else insert_obs_text

                    cursor.execute(insert_sql, (loco_id, section_id, s_no, loco_type, brake_type, railway_division, shed_name, inspection_date, insert_obs_text, status, remarks))

                debug_entry['action'] = 'inserted'
                debug_entry['finalHeight'] = new_height

                if image_paths and isinstance(image_paths, list):
                    for img_path in image_paths:
                        img_stmt = conn.cursor()
                        img_stmt.execute(
                            "INSERT INTO images (entity_type, loco_id, s_no, image_path, created_at) VALUES (%s, %s, %s, %s, NOW())",
                            ('radio_power', loco_id, s_no, img_path)
                        )
                        img_stmt.close()

            debug_info.append(debug_entry)

        return jsonify({'success': True, 'message': 'Observations and images updated successfully.', 'debug': debug_info})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating observations: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
