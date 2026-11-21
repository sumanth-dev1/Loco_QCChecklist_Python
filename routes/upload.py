import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os, uuid, base64, re
from flask import Blueprint, request, jsonify

upload_bp = Blueprint('upload', __name__)

def sanitize_and_save_image_path(img_path, upload_dir="uploads"):
    """
    Ensures that img_path is a valid server file path (e.g. 'uploads/img_xyz.jpg').
    If the client sent a base64 Data URI ('data:image/...;base64,...'),
    decodes it, writes it to disk in 'uploads/', and returns the new relative path.
    Also strips unwanted domain/port prefixes and ignores invalid blob: URLs.
    """
    if not img_path or not isinstance(img_path, str):
        return None

    img_path = img_path.strip()
    if not img_path:
        return None

    # Check if this is a base64 Data URL
    if img_path.startswith("data:image/") and ";base64," in img_path:
        try:
            header, encoded = img_path.split(";base64,", 1)
            ext = header.split("/")[-1].split(";")[0].split("+")[0].lower()
            if ext not in ["jpg", "jpeg", "png", "gif", "webp"]:
                ext = "jpg"
            os.makedirs(upload_dir, exist_ok=True)
            filename = f"img_b64_{uuid.uuid4().hex}.{ext}"
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(encoded))
            return f"uploads/{filename}"
        except Exception as e:
            print(f"[Warning] Failed to decode base64 image: {e}")
            return None

    # Discard non-server local previews if any slipped through without upload
    if img_path.startswith("blob:") or img_path.startswith("data:"):
        return None

    # Normalize to relative path: remove http://.../uploads/ prefix
    if "/uploads/" in img_path:
        img_path = "uploads/" + img_path.split("/uploads/")[-1]

    # Truncate if still unreasonably long to protect database
    if len(img_path) > 1000:
        return None

    return img_path

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
