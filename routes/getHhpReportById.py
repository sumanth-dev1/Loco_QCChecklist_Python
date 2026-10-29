import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify
from db import get_hhp_connection

getHhpReportById_bp = Blueprint('getHhpReportById', __name__)

@getHhpReportById_bp.route('/getHhpReportById', methods=['GET'])
def getHhpReportById():
    loco_id = (request.args.get('loco_id') or '').strip()
    if not loco_id:
        return jsonify({'success': False, 'message': 'Missing loco_id parameter.'})

    conn = None
    try:
        conn = get_hhp_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT Loco_Id as locoID, Loco_type as locoType, Brake_type as brakeType, Railway_Division as railwayDivision, Shed_name as shedName, inspection_Date as inspectionDate FROM loco WHERE Loco_Id = %s",
            (loco_id,)
        )
        loco_details = cursor.fetchone()

        if not loco_details:
            return jsonify({'success': False, 'message': f"No HHP locomotive details found for loco_id: {loco_id}"})

        transformed = {
            'locoID': str(loco_details['locoID']),
            'locoType': loco_details['locoType'],
            'brakeType': loco_details['brakeType'],
            'railwayDivision': loco_details['railwayDivision'],
            'shedName': loco_details['shedName'],
            'inspectionDate': str(loco_details['inspectionDate']) if loco_details['inspectionDate'] else None
        }

        return jsonify({'success': True, 'data': {'locoDetails': transformed}})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
