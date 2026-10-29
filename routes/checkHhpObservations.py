import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify
from db import get_hhp_connection

checkHhpObservations_bp = Blueprint('checkHhpObservations', __name__)

TABLE_NAMES = {
    1: 'document_verification_table',
    2: 'verify_serial_numbers_of_equipment_as_per_ic',
    3: 'loco_kavach',
    4: 'emi_filter_box',
    5: 'rib_cab_input_box',
    6: 'dmi_lp_ocip',
    7: 'rfid_ps_unit',
    8: 'loco_antenna_and_gps_gsm_antenna',
    9: 'pneumatic_fittings_and_ep_valve_cocks_fixing',
    10: 'pressure_sensors_installation_in_loco',
    11: 'iru_faviely_units_fixing_for_e70_type_loco',
    12: 'psjb_tpm_units_fixing_for_ccb_type_loco',
    13: 'sifa_valve_fixing_for_ccb_type_loco',
    14: 'pgs_and_speedo_meter_units_fixing',
    15: 'rfid_reader_assembly',
    16: 'earthing',
    17: 'radio_power'
}

@checkHhpObservations_bp.route('/checkHhpObservations', methods=['POST'])
def checkHhpObservations():
    data = request.get_json(silent=True) or {}

    if not all(k in data for k in ["locoId", "shedName", "railwayDivision", "sectionId"]):
        return jsonify({"error": "Missing required parameters", "received": data})

    loco_id = data["locoId"]
    shed_name = data.get("shedName") or ''
    railway_division = data.get("railwayDivision") or ''
    try:
        raw_sec = str(data["sectionId"]).replace('.0', '').replace('_0', '').split('_')[0].split('.')[0]
        section_id = int(raw_sec)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid section ID", "valid_sections": list(TABLE_NAMES.keys())})

    if section_id not in TABLE_NAMES:
        return jsonify({"error": "Invalid section ID", "valid_sections": list(TABLE_NAMES.keys())})

    table = TABLE_NAMES[section_id]

    conn = None
    try:
        conn = get_hhp_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(f"SELECT * FROM `{table}` WHERE loco_id = %s", (loco_id,))
        rows = cursor.fetchall()

        # Format dates/timestamps for JSON serialization
        for r in rows:
            for k, v in r.items():
                if hasattr(v, 'strftime'):
                    r[k] = str(v)

        exists = len(rows) > 0
        if exists:
            return jsonify({
                "status": "exists",
                "exists": True,
                "sectionId": section_id,
                "message": "Section is filled",
                "observations": rows
            })
        else:
            return jsonify({
                "status": "not_found",
                "exists": False,
                "sectionId": section_id,
                "message": f"No observations found for section {section_id}",
                "observations": []
            })
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()
