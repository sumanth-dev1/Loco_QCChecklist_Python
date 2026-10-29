import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify
from db import get_connection

getReportDetails_bp = Blueprint('getReportDetails', __name__)

@getReportDetails_bp.route('/getReportDetails', methods=['GET'])
def getReportDetails():
    loco_id = request.args.get('loco_id')
    if not loco_id:
        return jsonify({'success': False, 'message': 'Invalid request. Loco ID is required.'})

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM report WHERE file_name LIKE %s ORDER BY upload_date DESC LIMIT 1", (f"%{loco_id}%",))
        report = cursor.fetchone()

        if report:
            if report.get('upload_date'):
                report['upload_date'] = str(report['upload_date'])

            observations = {}
            from section_map import SECTION_TABLES
            for sec_num, table_name in SECTION_TABLES.items():
                try:
                    cursor.execute(f"SELECT * FROM {table_name} WHERE loco_id = %s", (loco_id,))
                    sec_obs = cursor.fetchall()
                    if sec_obs:
                        observations[f"section{sec_num}"] = sec_obs
                except Exception:
                    pass

            report['observations'] = observations
            return jsonify({'success': True, 'report': report})
        else:
            return jsonify({'success': False, 'message': 'Report not found for this loco.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
