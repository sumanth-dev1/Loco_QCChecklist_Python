import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import html, os
from flask import Blueprint, request, jsonify
from db import get_connection

generateReport_bp = Blueprint('generateReport', __name__)

TABLE_NAMES = [
    'document_verification_table', 'verify_serial_numbers_of_equipment_as_per_ic',
    'loco_kavach', 'emi_filter_box', 'rib_cab_input_box', 'dmi_lp_ocip',
    'rfid_ps_unit', 'loco_antenna_and_gps_gsm_antenna', 'pneumatic_fittings_and_ep_valve_cocks_fixing',
    'pressure_sensors_installation_in_loco', 'iru_faviely_units_fixing_for_e70_type_loco',
    'psjb_tpm_units_fixing_for_ccb_type_loco', 'sifa_valve_fixing_for_ccb_type_loco',
    'pgs_and_speedo_meter_units_fixing', 'rfid_reader_assembly', 'earthing', 'radio_power'
]

@generateReport_bp.route('/generateReport', methods=['POST'])
def generateReport():
    if request.method != 'POST':
        return jsonify({'success': False, 'message': 'Invalid request method'}), 405

    loco_id_raw = request.form.get('loco-id')
    railway_division_raw = request.form.get('railway-division') or ''
    shed_name_raw = request.form.get('shed-name') or ''

    if not loco_id_raw:
        return jsonify({'success': False, 'message': 'Missing loco-id in POST data'}), 200

    loco_id = html.escape(loco_id_raw)
    railway_division = html.escape(railway_division_raw)
    shed_name = html.escape(shed_name_raw)

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS migration_meta (loco_id VARCHAR(20) PRIMARY KEY, section8_migrated TINYINT DEFAULT 0, section8_subrows_migrated TINYINT DEFAULT 0)")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE verify_serial_numbers_of_equipment_as_per_ic ADD COLUMN barcode VARCHAR(255) NULL")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE verify_serial_numbers_of_equipment_as_per_ic ADD COLUMN barcode_status VARCHAR(50) NULL")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE migration_meta ADD COLUMN section8_subrows_migrated TINYINT DEFAULT 0")
        except Exception:
            pass

        # Check migration flag for this loco
        cursor.execute("SELECT section8_migrated, section8_subrows_migrated FROM migration_meta WHERE loco_id = %s", (loco_id,))
        meta = cursor.fetchone()
        needs_migration = not meta or not meta.get('section8_migrated')

        if needs_migration:
            cursor.execute("SELECT S_no, observation_text FROM loco_antenna_and_gps_gsm_antenna WHERE loco_id = %s AND S_no IN ('8.1', '8.7', '8.13', '8.13.1')", (loco_id,))
            rows = cursor.fetchall()
            should_shift = False
            for row in rows:
                text = (row.get('observation_text') or '').lower()
                if row.get('S_no') == '8.1' and 'gps antenna' in text:
                    should_shift = True
                if row.get('S_no') == '8.7' and 'conduit' in text:
                    should_shift = True

            if should_shift:
                mapping = {
                    '8.8': '8.14', '8.7.4': '8.13.4', '8.7.3': '8.13.3', '8.7.2': '8.13.2',
                    '8.7.1': '8.13.1', '8.7': '8.13', '8.6': '8.12', '8.5': '8.11',
                    '8.4': '8.10', '8.3': '8.9', '8.2': '8.8', '8.1': '8.7'
                }
                for old_sno, new_sno in mapping.items():
                    for tbl in TABLE_NAMES:
                        cursor.execute(f"UPDATE {tbl} SET S_no = %s WHERE loco_id = %s AND S_no = %s", (new_sno, loco_id, old_sno))
                    cursor.execute("UPDATE images SET S_no = %s WHERE loco_id = %s AND S_no = %s", (new_sno, loco_id, old_sno))

            cursor.execute("INSERT INTO migration_meta (loco_id, section8_migrated) VALUES (%s, 1) ON DUPLICATE KEY UPDATE section8_migrated = 1", (loco_id,))

        needs_subrow = not meta or not meta.get('section8_subrows_migrated')
        if needs_subrow:
            subrow_mapping = {'8.7.4': '8.13.4', '8.7.3': '8.13.3', '8.7.2': '8.13.2', '8.7.1': '8.13.1'}
            for old_sno, new_sno in subrow_mapping.items():
                cursor.execute("UPDATE loco_antenna_and_gps_gsm_antenna SET S_no = %s WHERE loco_id = %s AND TRIM(S_no) = %s", (new_sno, loco_id, old_sno))
                cursor.execute("UPDATE images SET S_no = %s WHERE loco_id = %s AND TRIM(S_no) = %s", (new_sno, loco_id, old_sno))

            cursor.execute("SELECT id, S_no, observation_text FROM loco_antenna_and_gps_gsm_antenna WHERE loco_id = %s AND (S_no LIKE '8.%%' OR S_no LIKE '14.%%' OR S_no LIKE '8.0.%%')", (loco_id,))
            for row in cursor.fetchall():
                text = row.get('observation_text') or ''
                new_sno = None
                if 'securely clamped to the roof using clamps welded to the rooftop' in text:
                    new_sno = '8.13.1'
                elif 'conduit is routed into the Loco cabin through the elbow pipe' in text:
                    new_sno = '8.13.2'
                elif 'conduit pipe and elbow are sourced from the Loco Kavach' in text:
                    new_sno = '8.13.3'
                elif 'RTV Silicone compound' in text:
                    new_sno = '8.13.4'

                if new_sno and row.get('S_no') != new_sno:
                    cursor.execute("UPDATE loco_antenna_and_gps_gsm_antenna SET S_no = %s WHERE id = %s", (new_sno, row['id']))
                    cursor.execute("UPDATE images SET S_no = %s WHERE loco_id = %s AND TRIM(S_no) = %s", (new_sno, loco_id, str(row['S_no']).strip()))

            cursor.execute("INSERT INTO migration_meta (loco_id, section8_subrows_migrated) VALUES (%s, 1) ON DUPLICATE KEY UPDATE section8_subrows_migrated = 1", (loco_id,))

        shed_condition = "shed_name = %s"
        shed_params = [shed_name]
        if 'Vadodara' in shed_name or 'Vadodhara' in shed_name or '(BRC)' in shed_name:
            shed_condition = "(shed_name LIKE '%%Vadodara%%' OR shed_name LIKE '%%Vadodhara%%' OR shed_name LIKE '%%(BRC)%%')"
            shed_params = []
        elif 'Vatva' in shed_name or '(VTA)' in shed_name:
            shed_condition = "(shed_name LIKE '%%Vatva%%' OR shed_name LIKE '%%(VTA)%%')"
            shed_params = []

        loco_details = None
        # Try matching with Division and Shed if provided
        if railway_division and shed_name:
            loco_query = f"SELECT Loco_Id as loco_id, Loco_type as loco_type, Brake_type as brake_type, Railway_Division as railway_division, Shed_name as shed_name, inspection_Date as inspection_date FROM loco WHERE Loco_Id = %s AND Railway_Division = %s AND {shed_condition}"
            params = [loco_id, railway_division] + shed_params
            cursor.execute(loco_query, params)
            loco_details = cursor.fetchone()

        # Fallback: Loco_Id is unique, so lookup by Loco_Id alone if Division/Shed mismatched or empty
        if not loco_details:
            cursor.execute("SELECT Loco_Id as loco_id, Loco_type as loco_type, Brake_type as brake_type, Railway_Division as railway_division, Shed_name as shed_name, inspection_Date as inspection_date FROM loco WHERE Loco_Id = %s", (loco_id,))
            loco_details = cursor.fetchone()

        if not loco_details:
            return jsonify({'success': False, 'message': f'Loco details not found for Loco ID: {loco_id}. Please check the ID or save loco info first.'}), 200

        if loco_details.get('inspection_date'):
            loco_details['inspection_date'] = str(loco_details['inspection_date'])

        cursor.execute("SELECT S_no, image_path FROM images WHERE loco_id = %s", (loco_id,))
        img_rows = cursor.fetchall()
        all_images = {}
        for r in img_rows:
            sno = r['S_no']
            if sno not in all_images:
                all_images[sno] = []
            all_images[sno].append(r['image_path'])

        observations = []
        host = request.host
        protocol = "https://" if request.is_secure else "http://"

        for table_name in TABLE_NAMES:
            barcode_select = ", barcode" if table_name == 'verify_serial_numbers_of_equipment_as_per_ic' else ", NULL as barcode"
            query = f"""SELECT S_no, observation_text, remarks, observation_status, section_id {barcode_select}
                      FROM {table_name}
                      WHERE loco_id = %s
                      ORDER BY
                        CAST(SUBSTRING_INDEX(S_no, '.', 1) AS UNSIGNED),
                        CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(S_no, '.', 2), '.', -1) AS UNSIGNED),
                        CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(S_no, '.', 3), '.', -1) AS UNSIGNED),
                        CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(S_no, '.', 4), '.', -1) AS UNSIGNED)"""
            cursor.execute(query, (loco_id,))
            tbl_obs = cursor.fetchall()

            for obs in tbl_obs:
                imgs_for_sno = all_images.get(obs['S_no'], [])
                valid_images = []
                for img_path in imgs_for_sno:
                    if img_path:
                        clean_path = str(img_path).replace('\\', '/').lstrip('/')
                        full_disk_path = os.path.join(os.getcwd(), clean_path)
                        if os.path.exists(full_disk_path) and clean_path.startswith('uploads/'):
                            valid_images.append(f"{protocol}{host}/{clean_path}")

                obs['images'] = valid_images
                observations.append(obs)

        return jsonify({
            'success': True,
            'locoDetails': loco_details,
            'observations': observations
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {e}'}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()
