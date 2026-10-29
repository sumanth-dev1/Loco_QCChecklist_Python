import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import base64, re, os, uuid
from flask import Blueprint, request
from db import get_connection

save_image_bp = Blueprint('save_image', __name__)

@save_image_bp.route('/save_image', methods=['POST'])
def save_image():
    if request.method == 'POST':
        image_data = request.form.get('imageData', '')
        if 'data:image/' not in image_data:
            return "Invalid image data."

        m = re.search(r'data:image/(.*?);base64,', image_data)
        if not m:
            return "Invalid image data."

        image_type = m.group(1)
        image_name = f"{uuid.uuid4().hex}.{image_type}"
        upload_dir = 'uploads/'
        os.makedirs(upload_dir, exist_ok=True)

        raw_b64 = image_data.split(';base64,')[-1]
        decoded = base64.b64decode(raw_b64)
        image_path = os.path.join(upload_dir, image_name).replace('\\', '/')

        with open(image_path, 'wb') as f:
            f.write(decoded)

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(buffered=True)
            cursor.execute("INSERT INTO observations (image_path) VALUES (%s)", (image_path,))
            return "Image uploaded and stored successfully!"
        except Exception as e:
            return f"Error uploading image: {e}"
        finally:
            if conn and conn.is_connected():
                conn.close()
    return ""
