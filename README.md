# Locomotive QC Checklist - Pure Python Backend

This project is a modern, pure Python web application for Locomotive Quality Control (QC) Inspection Checklists (supporting both Standard Electric Locomotives and Diesel HHP Locomotives) using Flask and Waitress WSGI.

---

## Key Highlights
- **100% Pure Python**: All server logic, routing, PDF report compilation, and session security run in Python (0 PHP files).
- **Dual Fleet Support**: Handles both Standard Electric Locos (`loco_info`) and Diesel HHP Locos (`hhp_loco_info`) with full 17-section parity.
- **XAMPP & Apache Independent**: Apache is no longer required. Multi-threaded Waitress WSGI serves HTTP traffic on port 5000.
- **Tablet & Mobile Friendly**: Technicians can complete inspections directly from workshop tablets or phones via Wi-Fi.
- **Zero Stale Cache**: Automated HTTP cache-control headers guarantee client browsers immediately receive updated code upon refresh.

---

## Quick Start on a New Machine

### 1. Prerequisites
- **Python 3.10+ / 3.12+** installed (check "Add python.exe to PATH" during installation)
- **MySQL Server** or **MariaDB** running on port 3306
- **Git** installed

### 2. Setup Instructions
```bash
# 1. Clone the repository
git clone <your-repository-url>
cd loco_qc_python

# 2. Create and activate a Python virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install required packages
pip install -r requirements.txt

# 4. Create your .env file
copy .env.example .env
# Edit .env and enter your MySQL password and a secure SECRET_KEY

# 5. Initialize both databases (loco_info and hhp_loco_info) with 1 command
python database/setup_database.py

# 6. Start the application
python run.py
```
Or simply double-click `start.bat` on Windows.

---

## Accessing from a Workshop Tablet ("Tab") or Mobile Device

You do **NOT** need to install Python, MySQL, or Git on the tablet.
1. Connect the tablet to the same Wi-Fi / Local Area Network as your host PC.
2. Find the host PC's Local IP address:
   - On Windows, open PowerShell and run `ipconfig`.
   - Look for **IPv4 Address** (e.g. `192.168.1.15`).
3. Open Google Chrome or Microsoft Edge on the tablet and go to:
   ```
   http://192.168.1.15:5000/
   ```
4. Log in and perform inspections. All observations and photos sync immediately with the central database.

---

## Project Structure
- `app.py`: Core Flask application registering all 71 modular blueprints and static file handlers.
- `run.py`: Production Waitress WSGI runner listening on `0.0.0.0:5000`.
- `config.py` & `db.py`: Centralized environment loader and MySQL connection pooling.
- `database/`:
  - `loco_info_schema.sql`: Full schema for Standard Electric locomotives (24 tables).
  - `hhp_loco_info_schema.sql`: Full schema for Diesel HHP locomotives (22 tables).
  - `setup_database.py`: 1-click database creator and importer.
- `routes/`: Modular Flask blueprints:
  - Authentication & Users: `login.py`, `create_user.py`, `edit_user.py`, `view_users.py`, `verify_admin.py`
  - Standard Sections 1.0 - 17.0: `section1_0.py` to `section17_0.py`
  - HHP Sections 1.0 - 17.0: `hhp_section1_0.py` to `hhp_section17_0.py`
  - Observations & Timing: `checkInitialTiming.py`, `checkObservations.py`, `store_observation.py`, `updateObservations.py`, `fetch_observations.py`, etc.
  - Reports & Signatures: `generateReport.py`, `generateHhpReport.py`, `viewReports.py`, `uploadSignature.py`, `upload.py`
- `static/`: HTML templates, CSS styles, and client JavaScript (`script.js`, `script_hhp.js`).
- `uploads/`: Central store for inspection images and digital signatures.
