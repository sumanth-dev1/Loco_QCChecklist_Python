# Locomotive QC Python Application (Loco QC)

A pure Python 3.12+ / MySQL web application migrated from PHP/Apache.
This application operates completely independently of XAMPP and Apache.

---

## 🚀 Key Features

* **Zero PHP, Zero Apache**: Handled natively by Python (Flask + Waitress WSGI server).
* **Dual Fleet Support**: Handles both Standard Electric Locomotives (`loco_info`) and Diesel HHP Locomotives (`hhp_loco_info`) across all 17 sections.
* **No Port Conflicts**: Runs on port `5000` (allowing Loco QC on port `5000` and Station QC on `5001` to run simultaneously).
* **Zero Frontend Modifications**: Identical UI, checklists, auto-save timers, scanner support, and observation sync.
* **Tablet & Mobile Friendly**: Technicians can complete inspections directly from workshop tablets or phones via Wi-Fi.
* **Safe 1-Click Database Engine**: Automated non-destructive setup and migration for both fleet databases (`setup_database.py`).
* **All-in-One Smart Launcher**: Double-click `start.bat` to auto-create `venv`, install packages, verify database, and open browser.

---

## ⚡ 1-Click Fast Setup (Recommended)

Simply double-click **`start.bat`**!

It will automatically:
1. Detect Python (or the Windows Python launcher `py`) and create the virtual environment (`.\venv`).
2. Upgrade `pip` and install all dependencies from `requirements.txt`.
3. Auto-generate the `.env` configuration file (if not present).
4. Auto-initialize and migrate both `loco_info` and `hhp_loco_info` databases and all tables without data loss.
5. Launch the Waitress server on port `5000` and automatically open **http://localhost:5000/** in your browser!

*(Default admin test login: username `12345`, password `12345`)*

---

## 📁 Directory Structure

```
loco_qc_python/
├── .env.example                 # Template for environment configuration
├── config.py                    # Environment configuration loader
├── db.py                        # Centralized MySQL connection pool
├── app.py                       # Main Flask application & route registrations (71 blueprints)
├── run.py                       # Waitress production runner (Port 5000)
├── requirements.txt             # Project Python dependencies
├── start.bat                    # All-in-one smart setup & browser launcher
├── stop.bat                     # Server shutdown script
├── launch_silent.vbs            # Silent background launcher
├── create_shortcut.ps1          # Desktop shortcut creator
├── database/
│   ├── loco_info_schema.sql     # Electric Locomotive schema (24 tables)
│   ├── hhp_loco_info_schema.sql # Diesel HHP Locomotive schema (22 tables)
│   └── setup_database.py        # Automated dual-database setup & migration script
├── routes/                      # Modular Python blueprints (all 17 sections, auth, reports)
├── static/                      # Frontend HTML, CSS, JS, and logos
└── uploads/                     # Storage for inspection photos and digital signatures
```

---

## 🛠️ Manual Installation & Setup (Alternative)

### 1. Prerequisites
* Python 3.10+ (Recommended Python 3.12)
* MySQL Server (Standalone MySQL Community Server 8.0, MariaDB, or XAMPP MySQL running on port 3306)

### 2. Environment Configuration
Copy `.env.example` to `.env` and fill in your MySQL credentials:
```cmd
copy .env.example .env
```
Edit `.env`:
```ini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=loco_info
HHP_DB_NAME=hhp_loco_info
SECRET_KEY=loco_qc_secure_secret_key_2026
```
*(Note for standard XAMPP: default user is `root` with no password, so leave `DB_PASSWORD=` blank).*

### 3. Create Virtual Environment & Install Dependencies
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Database Setup
Run the automated migration engine:
```cmd
python database/setup_database.py
```

---

## 🏃 Running the Application

### Option A: One-Click (Windows)
Double-click `start.bat` (or use the Desktop shortcut created via `create_shortcut.ps1`).

### Option B: Command Line
```cmd
python run.py
```

To stop the server:
```cmd
stop.bat
```

---

## 📱 Accessing from a Workshop Tablet ("Tab") or Mobile Device

You do **NOT** need to install Python, MySQL, or Git on the tablet.
1. Connect the tablet to the same Wi-Fi / Local Area Network as the host PC.
2. Find the host PC's IPv4 address by running `ipconfig` in Command Prompt (e.g. `192.168.1.15`).
3. On the tablet browser (Chrome / Edge), navigate to:
   ```
   http://192.168.1.15:5000/
   ```
4. Log in and perform inspections. All observations and photos sync immediately with the central database.

---

## 🌐 Application URLs

* **Dashboard / Home**: [http://localhost:5000/](http://localhost:5000/)
* **Login**: [http://localhost:5000/login.html](http://localhost:5000/login.html)
* **Electric Loco Checklist**: [http://localhost:5000/create.html](http://localhost:5000/create.html)
* **HHP Diesel Checklist**: [http://localhost:5000/create_hhp.html](http://localhost:5000/create_hhp.html)
* **Reports**: [http://localhost:5000/viewReports](http://localhost:5000/viewReports)
* **Health Check**: [http://localhost:5000/health](http://localhost:5000/health)
