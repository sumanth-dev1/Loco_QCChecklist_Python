import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify
from db import get_connection

fetch_section_data_bp = Blueprint('fetch_section_data', __name__)

@fetch_section_data_bp.route('/fetch_section_data', methods=['GET'])
def fetch_section_data():
    section_id = request.args.get('section_id')
    if not section_id:
        return jsonify({"error": "No section ID provided"})

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM sections WHERE section_id = %s", (section_id,))
        rows = cursor.fetchall()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()
