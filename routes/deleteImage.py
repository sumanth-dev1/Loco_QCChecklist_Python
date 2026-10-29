import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
from flask import Blueprint, request, jsonify
from db import get_connection

deleteImage_bp = Blueprint('deleteImage', __name__)

@deleteImage_bp.route('/deleteImage', methods=['POST'])
def deleteImage():
    if request.method != 'POST':
        return jsonify({'success': False, 'message': 'Invalid request method'})

    data = request.get_json(silent=True) or {}
    loco_id = data.get('loco_id')
    s_no = data.get('s_no')
    img_path = data.get('imgPath')

    if not all([loco_id, s_no, img_path]):
        return jsonify({'success': False, 'message': 'Missing parameters'})

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        cursor.execute("SELECT * FROM images WHERE loco_id = %s AND s_no = %s AND image_path = %s", (loco_id, s_no, img_path))
        record = cursor.fetchone()

        if record:
            cursor.execute("DELETE FROM images WHERE loco_id = %s AND s_no = %s AND image_path = %s", (loco_id, s_no, img_path))

            full_path = os.path.join(os.getcwd(), img_path)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except Exception:
                    pass

            return jsonify({'success': True, 'message': 'Image deleted successfully.'})
        else:
            return jsonify({'success': False, 'message': 'Image record not found in database.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {e}'})
    finally:
        if conn and conn.is_connected():
            conn.close()
