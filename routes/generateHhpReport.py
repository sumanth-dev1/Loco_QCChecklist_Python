import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import html
from flask import Blueprint, request, jsonify
from db import get_hhp_connection

generateHhpReport_bp = Blueprint('generateHhpReport', __name__)

TABLE_NAMES = [
    'document_verification_table', 'verify_serial_numbers_of_equipment_as_per_ic',
    'loco_kavach', 'emi_filter_box', 'rib_cab_input_box', 'dmi_lp_ocip',
    'rfid_ps_unit', 'loco_antenna_and_gps_gsm_antenna', 'pneumatic_fittings_and_ep_valve_cocks_fixing',
    'pressure_sensors_installation_in_loco', 'iru_faviely_units_fixing_for_e70_type_loco',
    'psjb_tpm_units_fixing_for_ccb_type_loco', 'sifa_valve_fixing_for_ccb_type_loco',
    'pgs_and_speedo_meter_units_fixing', 'rfid_reader_assembly', 'earthing', 'radio_power'
]

@generateHhpReport_bp.route('/generateHhpReport', methods=['POST'])
def generateHhpReport():
    if request.method != 'POST':
        return jsonify({'success': False, 'message': 'Invalid request method'}), 405

    loco_id_raw = request.form.get('loco-id') or request.form.get('loco_id')
    if not loco_id_raw:
        return jsonify({'success': False, 'message': 'Missing loco-id in POST data'}), 400

    loco_id = html.escape(str(loco_id_raw).strip())

    conn = None
    try:
        conn = get_hhp_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        cursor.execute(
            """SELECT Loco_Id AS loco_id, Loco_Id AS locoID, 
                      Loco_type AS loco_type, Loco_type AS locoType, 
                      Brake_type AS brake_type, Brake_type AS brakeType, 
                      Railway_Division AS railway_division, Railway_Division AS railwayDivision, 
                      Shed_name AS shed_name, Shed_name AS shedName, 
                      inspection_Date AS inspection_date, inspection_Date AS inspectionDate 
               FROM loco WHERE Loco_Id = %s""",
            (loco_id,)
        )
        loco_details = cursor.fetchone()

        if not loco_details:
            return jsonify({'success': False, 'message': f"No locomotive found with ID {loco_id}"}), 200

        if loco_details.get('inspection_date'):
            loco_details['inspection_date'] = str(loco_details['inspection_date'])
            loco_details['inspectionDate'] = str(loco_details['inspectionDate'])

        host = request.host
        protocol = "https://" if request.is_secure else "http://"

        all_observations = []
        for tbl in TABLE_NAMES:
            barcode_select = ", barcode" if tbl == 'verify_serial_numbers_of_equipment_as_per_ic' else ", NULL as barcode"
            sql = f"""SELECT S_no, observation_text, observation_status, remarks, image_path, created_at, updated_at, section_id {barcode_select} 
                      FROM `{tbl}` WHERE loco_id = %s
                      ORDER BY
                        CAST(SUBSTRING_INDEX(S_no, '.', 1) AS UNSIGNED),
                        CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(S_no, '.', 2), '.', -1) AS UNSIGNED),
                        CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(S_no, '.', 3), '.', -1) AS UNSIGNED),
                        CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(S_no, '.', 4), '.', -1) AS UNSIGNED)"""
            cursor.execute(sql, (loco_id,))
            rows = cursor.fetchall()

            for row in rows:
                s_no = str(row['S_no'])
                img_cur = conn.cursor(dictionary=True, buffered=True)
                img_cur.execute("SELECT image_path FROM images WHERE loco_id = %s AND s_no = %s", (loco_id, s_no))
                img_rows = img_cur.fetchall()
                img_paths = [r['image_path'] for r in img_rows if r.get('image_path')]
                img_cur.close()

                if not img_paths and row.get('image_path'):
                    img_paths = [p.strip() for p in str(row['image_path']).split(',') if p.strip()]

                valid_web_images = []
                for ip in img_paths:
                    clean_p = str(ip).replace('\\', '/').lstrip('/')
                    if os.path.exists(os.path.join(os.getcwd(), clean_p)):
                        valid_web_images.append(f"{protocol}{host}/{clean_p}")
                    else:
                        valid_web_images.append(clean_p)

                all_observations.append({
                    'S_no': row['S_no'],
                    'observation_text': row['observation_text'],
                    'observation_status': row['observation_status'],
                    'remarks': row['remarks'],
                    'image_path': ','.join(img_paths) if img_paths else (row['image_path'] or ''),
                    'image_paths': img_paths,
                    'images': valid_web_images,
                    'barcode': row.get('barcode'),
                    'created_at': str(row['created_at']) if row.get('created_at') else None,
                    'updated_at': str(row['updated_at']) if row.get('updated_at') else None,
                    'section_id': row.get('section_id')
                })

        return jsonify({
            'success': True,
            'locoDetails': loco_details,
            'observations': all_observations
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {e}'}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()
