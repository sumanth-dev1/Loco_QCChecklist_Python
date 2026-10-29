import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, jsonify, send_from_directory
from mysql.connector import Error as MySQLError

import config
import db

import logging
logging.basicConfig(
    filename='app_errors.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)

app = Flask(__name__, static_folder='static')
app.secret_key = config.SECRET_KEY

# Register all 1-to-1 endpoint blueprints
from routes.connect import connect_bp
from routes.login import login_bp
from routes.create_user import create_user_bp
from routes.edit_user import edit_user_bp
from routes.view_users import view_users_bp
from routes.verify_admin import verify_admin_bp

from routes.section1_0 import section1_0_bp
from routes.section2_0 import section2_0_bp
from routes.section3_0 import section3_0_bp
from routes.section4_0 import section4_0_bp
from routes.section5_0 import section5_0_bp
from routes.section6_0 import section6_0_bp
from routes.section7_0 import section7_0_bp
from routes.section8_0 import section8_0_bp
from routes.section9_0 import section9_0_bp
from routes.section10_0 import section10_0_bp
from routes.section11_0 import section11_0_bp
from routes.section12_0 import section12_0_bp
from routes.section13_0 import section13_0_bp
from routes.section14_0 import section14_0_bp
from routes.section15_0 import section15_0_bp
from routes.section16_0 import section16_0_bp
from routes.section17_0 import section17_0_bp

from routes.checkInitialTiming import checkInitialTiming_bp
from routes.checkObservations import checkObservations_bp
from routes.fetchObservations import fetchObservations_bp
from routes.fetch_observations import fetch_observations_bp
from routes.fetch_section_data import fetch_section_data_bp
from routes.getObservations import getObservations_bp
from routes.get_loco_timings import get_loco_timings_bp
from routes.store_observation import store_observation_bp
from routes.updateObservations import updateObservations_bp
from routes.update_completed_time import update_completed_time_bp
from routes.observation import observation_bp

from routes.deleteImage import deleteImage_bp
from routes.edit_report import edit_report_bp
from routes.fetchReports import fetchReports_bp
from routes.generateReport import generateReport_bp
from routes.getLocoDetails import getLocoDetails_bp
from routes.getNextVersion import getNextVersion_bp
from routes.getReportById import getReportById_bp
from routes.getReportDetails import getReportDetails_bp
from routes.save_image import save_image_bp
from routes.save_report import save_report_bp
from routes.update_version import update_version_bp
from routes.upload import upload_bp
from routes.uploadReport import uploadReport_bp
from routes.uploadSignature import uploadSignature_bp
from routes.viewReports import viewReports_bp
from routes.db_migration import db_migration_bp
from routes.upload_to_wfms import upload_to_wfms_bp
from routes.wfms_proxy import wfms_proxy_bp
from routes.db_admin import db_admin_bp

# HHP Specific Blueprints
from routes.connect_hhp import connect_hhp_bp
from routes.checkHhpInitialTiming import checkHhpInitialTiming_bp
from routes.get_hhp_loco_timings import get_hhp_loco_timings_bp
from routes.checkHhpObservations import checkHhpObservations_bp
from routes.fetch_hhp_observations import fetch_hhp_observations_bp
from routes.save_hhp_observation import save_hhp_observation_bp
from routes.updateHhpObservations import updateHhpObservations_bp
from routes.update_hhp_completed_time import update_hhp_completed_time_bp
from routes.generateHhpReport import generateHhpReport_bp
from routes.getHhpReportById import getHhpReportById_bp
from routes.uploadHhpReport import uploadHhpReport_bp
from routes.viewHhpReports import viewHhpReports_bp

from routes.hhp_section1_0 import hhp_section1_0_bp
from routes.hhp_section2_0 import hhp_section2_0_bp
from routes.hhp_section3_0 import hhp_section3_0_bp
from routes.hhp_section4_0 import hhp_section4_0_bp
from routes.hhp_section5_0 import hhp_section5_0_bp
from routes.hhp_section6_0 import hhp_section6_0_bp
from routes.hhp_section7_0 import hhp_section7_0_bp
from routes.hhp_section8_0 import hhp_section8_0_bp
from routes.hhp_section9_0 import hhp_section9_0_bp
from routes.hhp_section10_0 import hhp_section10_0_bp
from routes.hhp_section11_0 import hhp_section11_0_bp
from routes.hhp_section12_0 import hhp_section12_0_bp
from routes.hhp_section13_0 import hhp_section13_0_bp
from routes.hhp_section14_0 import hhp_section14_0_bp
from routes.hhp_section15_0 import hhp_section15_0_bp
from routes.hhp_section16_0 import hhp_section16_0_bp
from routes.hhp_section17_0 import hhp_section17_0_bp

blueprints = [
    connect_bp, login_bp, create_user_bp, edit_user_bp, view_users_bp, verify_admin_bp,
    section1_0_bp, section2_0_bp, section3_0_bp, section4_0_bp, section5_0_bp, section6_0_bp,
    section7_0_bp, section8_0_bp, section9_0_bp, section10_0_bp, section11_0_bp, section12_0_bp,
    section13_0_bp, section14_0_bp, section15_0_bp, section16_0_bp, section17_0_bp,
    checkInitialTiming_bp, checkObservations_bp, fetchObservations_bp, fetch_observations_bp,
    fetch_section_data_bp, getObservations_bp, get_loco_timings_bp, store_observation_bp,
    updateObservations_bp, update_completed_time_bp, observation_bp, deleteImage_bp,
    edit_report_bp, fetchReports_bp, generateReport_bp, getLocoDetails_bp, getNextVersion_bp,
    getReportById_bp, getReportDetails_bp, save_image_bp, save_report_bp, update_version_bp,
    upload_bp, uploadReport_bp, uploadSignature_bp, viewReports_bp, db_migration_bp,
    upload_to_wfms_bp, wfms_proxy_bp, db_admin_bp,
    # HHP Blueprints
    connect_hhp_bp, checkHhpInitialTiming_bp, get_hhp_loco_timings_bp, checkHhpObservations_bp,
    fetch_hhp_observations_bp, save_hhp_observation_bp, updateHhpObservations_bp,
    update_hhp_completed_time_bp, generateHhpReport_bp, getHhpReportById_bp, uploadHhpReport_bp,
    viewHhpReports_bp, hhp_section1_0_bp, hhp_section2_0_bp, hhp_section3_0_bp, hhp_section4_0_bp,
    hhp_section5_0_bp, hhp_section6_0_bp, hhp_section7_0_bp, hhp_section8_0_bp, hhp_section9_0_bp,
    hhp_section10_0_bp, hhp_section11_0_bp, hhp_section12_0_bp, hhp_section13_0_bp,
    hhp_section14_0_bp, hhp_section15_0_bp, hhp_section16_0_bp, hhp_section17_0_bp
]

for bp in blueprints:
    app.register_blueprint(bp)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Flask backend active"})


@app.route("/test-db")
def test_db():
    try:
        tables = db.list_tables()
        return jsonify({
            "success": True,
            "database": config.DB_NAME,
            "tables": tables,
            "table_count": len(tables),
        })
    except MySQLError as e:
        return jsonify({
            "success": False,
            "message": f"MySQL connection/query failed: {e}",
        }), 500


# Static and uploaded files serving
@app.route("/uploads/<path:filename>")
def serve_uploads(filename):
    uploads_dir = os.path.abspath("uploads")
    target_file = os.path.join(uploads_dir, filename)
    if os.path.exists(target_file) and os.path.isfile(target_file):
        return send_from_directory(uploads_dir, filename)

    # Legacy XAMPP fallback: if image was uploaded in previous XAMPP setup, serve it
    xampp_candidates = [
        os.path.join(r"C:\xampp\htdocs", "uploads", filename),
        os.path.join(r"C:\xampp\htdocs", "loco_qc", "uploads", filename),
        os.path.join(r"C:\xampp\htdocs", "QCchecklist", "uploads", filename),
        os.path.join(r"C:\xampp\htdocs", "qc", "uploads", filename),
        os.path.join(r"C:\xampp\htdocs", "loco_qc_python", "uploads", filename),
    ]
    for candidate in xampp_candidates:
        if os.path.exists(candidate) and os.path.isfile(candidate):
            return send_from_directory(os.path.dirname(candidate), os.path.basename(candidate))

    return jsonify({"error": "File not found"}), 404


@app.route("/")
def serve_root():
    return send_from_directory(os.path.abspath("static"), "index.html")


@app.route("/<path:path>")
def serve_static(path):
    if not path or path.endswith("/"):
        path += "index.html"

    # Check uploads
    if path.startswith("uploads/"):
        return send_from_directory(os.path.abspath("."), path)

    static_dir = os.path.abspath("static")
    target_file = os.path.join(static_dir, path)

    if os.path.exists(target_file) and os.path.isfile(target_file):
        return send_from_directory(static_dir, path)

    return jsonify({"error": "File not found"}), 404


@app.after_request
def add_cache_control_headers(response):
    """
    Prevent browsers from serving stale cached JavaScript and CSS
    when code updates are deployed.
    """
    if "Cache-Control" not in response.headers:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    from waitress import serve
    from database.setup_database import setup_or_migrate
    try:
        setup_or_migrate()
    except Exception as e:
        print(f"Database pre-check notice: {e}")
    print("Starting Waitress production server on port 5000...")
    serve(app, host="0.0.0.0", port=5000)