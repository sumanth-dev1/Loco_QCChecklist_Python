import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os, uuid
from flask import Blueprint, request, jsonify

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files.getlist('images') or request.files.getlist('images[]')
        if not files and 'images' in request.files:
            files = [request.files['images']]

        upload_dir = 'uploads/'
        os.makedirs(upload_dir, exist_ok=True)
        uploaded_files = []

        for file in files:
            if file and file.filename != '':
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
                filename = f"img_{uuid.uuid4().hex}.{ext}"
                upload_path = os.path.join(upload_dir, filename)
                file.save(upload_path)
                uploaded_files.append(f"uploads/{filename}")

        if uploaded_files:
            return jsonify({"success": True, "file_paths": uploaded_files})
        else:
            return jsonify({"success": False, "message": "No valid images uploaded."})

    return jsonify({"success": False, "message": "No files received."})
