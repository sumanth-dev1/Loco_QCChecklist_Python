import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import re
from flask import Blueprint, session, render_template_string, request
from db import get_hhp_connection, get_connection

viewHhpReports_bp = Blueprint('viewHhpReports', __name__)

VIEW_HHP_REPORTS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reports - HBL Engineering Ltd. (HHP LOCO)</title>
  <style>
    body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 0; }
    h1, h2 { text-align: center; margin: 0; }
    .container { padding: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    table, th, td { border: 1px solid #ddd; }
    th, td { padding: 10px; text-align: left; }
    th { background-color: #00457C; color: white; }
    td a { color: #00457C; text-decoration: none; }
    td a:hover { text-decoration: underline; }
    .btn { padding: 5px 10px; margin: 5px; cursor: pointer; color: white; border: none; border-radius: 5px; display: inline-block; }
    .view-btn { background-color: #17a2b8; }
    .edit-btn { background-color: #ffc107; }
    .download-btn { background-color: #28a745; }
    .back-btn { background-color: #6c757d; }
    .status-label { padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .completed { color: green; background-color: #d3ffd3; }
    .not-completed { color: red; background-color: #ffd3d3; }
    .profile { position: absolute; right: 20px; color: white; font-size: 14px; }
    #search-input { padding: 10px; width: 300px; margin-top: 20px; }
    
    .upload-btn { background-color: #6f42c1; color: white; border: none; padding: 5px 10px; margin: 5px; cursor: pointer; border-radius: 5px; display: inline-block; }
    .upload-btn:hover { background-color: #5a32a3; }
    
    .wfms-modal {
        display: none;
        position: fixed;
        z-index: 3000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.7);
        justify-content: center;
        align-items: center;
    }
    .wfms-modal-content {
        background-color: #fff;
        padding: 25px;
        border-radius: 8px;
        width: 400px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .wfms-modal-header {
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
        margin-bottom: 15px;
        font-size: 1.2rem;
        font-weight: bold;
        color: #6f42c1;
    }
    .wfms-form-group {
        margin-bottom: 15px;
        text-align: left;
    }
    .wfms-form-group label {
        display: block;
        margin-bottom: 5px;
        font-weight: 600;
    }
    .wfms-form-group input, .wfms-form-group select {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-sizing: border-box;
    }
    .wfms-btn-row {
        display: flex;
        gap: 10px;
        justify-content: flex-end;
        margin-top: 20px;
    }
    .loader {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #6f42c1;
        border-radius: 50%;
        width: 16px;
        height: 16px;
        animation: spin 2s linear infinite;
        display: inline-block;
        vertical-align: middle;
        margin-right: 8px;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>

<header style="display: flex; align-items: center; justify-content: center; background-color: #00457C; color: white; padding: 20px; position: relative;">
    <img src="hbl_logo.jpg" alt="HBL Engineering Ltd. Logo" style="position: absolute; left: 20px; height: 50px;">
    <div>
      <h1>HBL Engineering Ltd.</h1>
      <h2>Electronics Group (HHP LOCO)</h2>
    </div>
    <div class="profile">User: {{ username }} | Employee: {{ employee_name }}</div>
</header>

<div class="container">
    <a href="index.html" class="btn back-btn">Back to Home</a>
    
    <div style="text-align: right;">
      <input type="text" id="search-input" placeholder="Search by Loco ID..." autocomplete="new-password" name="search_loco_no_autofill">
    </div>
    
    <h2>Your Uploaded HHP LOCO Reports</h2>
    <table id="report-table">
        <thead>
            <tr>
                <th>Report</th>
                <th>Upload Date</th>
                <th>Upload Time</th>
                <th>User ID</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
        {% if reports %}
            {% for report in reports %}
                <tr data-loco-id="{{ report.loco_id }}">
                    <td>{{ report.file_name }}</td>
                    <td>{{ report.upload_date_fmt }}</td>
                    <td>{{ report.upload_time }}</td>
                    <td>{{ report.user_id }}</td>
                    <td>{{ report.status_label|safe }}</td>
                    <td>
                        <a href="uploads/reports/{{ report.file_name }}" class="btn view-btn" target="_blank">View</a>
                        <a href="create_hhp.html?loco_id={{ report.loco_id }}" class="btn edit-btn" target="_blank">Edit</a>
                        <a href="uploads/reports/{{ report.file_name }}" download class="btn download-btn" target="_blank">Download</a>
                        <button class="btn upload-btn" onclick="openWFMSLogin(event, '{{ report.id }}', '{{ report.loco_id }}')">Push to Loco WFMS</button>
                    </td>
                </tr>
            {% endfor %}
        {% else %}
            <tr>
                <td colspan="6" style="text-align: center; padding: 20px; color: #666; font-weight: bold;">No HHP reports available.</td>
            </tr>
        {% endif %}
        </tbody>
    </table>
</div>

<div id="wfmsLoginModal" class="wfms-modal">
    <div class="wfms-modal-content">
        <div class="wfms-modal-header">Login to Loco WFMS</div>
        <div id="login_error" style="color:red; font-size:0.9rem; margin-bottom:10px; display:none;"></div>
        <div class="wfms-form-group">
            <label for="wfms_user">Username</label>
            <input type="text" id="wfms_user" placeholder="Enter your credentials">
        </div>
        <div class="wfms-form-group">
            <label for="wfms_pass">Password</label>
            <input type="password" id="wfms_pass" placeholder="Enter your password">
        </div>
        <div class="wfms-btn-row">
            <button class="btn back-btn" onclick="closeWFMSModal('wfmsLoginModal')">Cancel</button>
            <button class="btn upload-btn" id="loginBtn" onclick="doWFMSLogin()">Login & Next</button>
        </div>
    </div>
</div>

<div id="wfmsLocoModal" class="wfms-modal">
    <div class="wfms-modal-content">
        <div class="wfms-modal-header">Select Loco Assignment</div>
        <div id="loco_status_text" style="font-size:0.95rem; margin-bottom:15px; line-height:1.5; text-align:left;">
            Verifying assignment...
        </div>
        <div class="wfms-form-group" id="locoSelectGroup" style="display:none;">
            <label for="wfms_loco_select" style="font-weight:600; display:block; margin-bottom:5px;">Select Assigned Loco</label>
            <select id="wfms_loco_select" onchange="onLocoSelected()" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:4px; font-size:0.95rem;">
                <option value="" disabled selected>Select a Loco</option>
            </select>
        </div>
        <div class="wfms-form-group" id="docSelectGroup" style="display:none; margin-top:10px;">
            <label for="wfms_doc_select" style="font-weight:600; display:block; margin-bottom:5px;">Document Slot</label>
            <select id="wfms_doc_select" onchange="onDocSelected()" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:4px; font-size:0.95rem;">
            </select>
        </div>
        <div id="verification_details" style="font-size:0.9rem; margin-top:15px; line-height:1.4; text-align:left;"></div>
        <div class="wfms-btn-row" style="margin-top:20px;">
            <button class="btn back-btn" onclick="closeWFMSModal('wfmsLocoModal')">Cancel</button>
            <button class="btn upload-btn" id="pushBtn" onclick="doFinalPush()" style="display:none;">Push Report</button>
        </div>
    </div>
</div>

<script>
  function clearSearchAutofill() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.value = '';
      searchInput.dispatchEvent(new Event('input'));
    }
  }

  window.addEventListener('DOMContentLoaded', () => {
    setTimeout(clearSearchAutofill, 50);
    setTimeout(clearSearchAutofill, 200);
    setTimeout(clearSearchAutofill, 500);
  });
  window.addEventListener('load', clearSearchAutofill);
  window.addEventListener('pageshow', clearSearchAutofill);

  window.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const tableRows = document.querySelectorAll('#report-table tbody tr');

    if (searchInput) {
      searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        tableRows.forEach(row => {
          const text = row.innerText.toLowerCase();
          row.style.display = text.includes(query) ? '' : 'none';
        });
      });
    }
  });

  let currentReportId = null;
  let currentLocoId = null;
  let wfmsToken = null;
  let assignedActivities = [];
  let targetActivityId = null;
  let targetDocId = null;

  function openWFMSLogin(event, reportId, locoId) {
    if (!navigator.onLine) {
        alert("No internet connection. Please check your connectivity to push to WFMS.");
        return;
    }
    currentReportId = reportId;
    currentLocoId = locoId;
    
    document.getElementById('wfms_user').value = '';
    document.getElementById('wfms_pass').value = '';
    document.getElementById('login_error').style.display = 'none';
    
    document.getElementById('wfmsLoginModal').style.display = 'flex';
  }

  function closeWFMSModal(id) {
    document.getElementById(id).style.display = 'none';
  }

  async function doWFMSLogin() {
    const user = document.getElementById('wfms_user').value.trim();
    const pass = document.getElementById('wfms_pass').value.trim();
    const errorDiv = document.getElementById('login_error');
    const btn = document.getElementById('loginBtn');

    if (!user || !pass) {
        errorDiv.innerText = "Please enter WFMS credentials";
        errorDiv.style.display = 'block';
        return;
    }

    errorDiv.style.display = 'none';
    btn.disabled = true;
    btn.innerHTML = '<span class="loader"></span> Connecting...';

    try {
        const response = await fetch('wfms_proxy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `action=login&user=${encodeURIComponent(user)}&pass=${encodeURIComponent(pass)}`
        });
        const result = await response.json();

        if (result.status && result.data && result.data.token) {
            wfmsToken = result.data.token;
            closeWFMSModal('wfmsLoginModal');
            verifyLocoAndGetDetails();
        } else {
            errorDiv.innerText = result.message || "Invalid WFMS credentials";
            errorDiv.style.display = 'block';
        }
    } catch (e) {
        errorDiv.innerText = "Error connecting to WFMS Server";
        errorDiv.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.innerText = "Login & Next";
    }
  }

  async function verifyLocoAndGetDetails() {
    const modal = document.getElementById('wfmsLocoModal');
    const statusText = document.getElementById('loco_status_text');
    const pushBtn = document.getElementById('pushBtn');
    const selectGroup = document.getElementById('locoSelectGroup');
    const docSelectGroup = document.getElementById('docSelectGroup');
    const select = document.getElementById('wfms_loco_select');
    const detailsDiv = document.getElementById('verification_details');
    
    modal.style.display = 'flex';
    pushBtn.style.display = 'none';
    selectGroup.style.display = 'none';
    docSelectGroup.style.display = 'none';
    detailsDiv.innerHTML = '';
    statusText.innerHTML = `<span class="loader"></span> Fetching active assignments from Loco WFMS...`;

    try {
        const response = await fetch('wfms_proxy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `action=get_assignments&token=${encodeURIComponent(wfmsToken)}`
        });
        const result = await response.json();

        if (!result.status || !result.data || !result.data.data) {
            statusText.innerHTML = `<span style="color:red;">Error fetching assignments from Loco WFMS: ${result.message || 'Unknown error'}</span>`;
            return;
        }

        assignedActivities = result.data.data;
        const matchingActs = assignedActivities.filter(act => act.loco && act.loco.number);

        if (matchingActs.length === 0) {
            statusText.innerHTML = `<span style="color:red;">No active assignments found on your dashboard.</span>`;
            return;
        }

        select.innerHTML = '<option value="" disabled selected>Select an Activity Assignment</option>';
        let autoSelectedId = null;
        matchingActs.forEach(act => {
            const opt = document.createElement('option');
            opt.value = act._id;
            opt.text = `Loco #${act.loco.number} - ${act.name}`;
            const cleanActLoco = String(act.loco.number).replace(/^0+/, '');
            const cleanCurLoco = String(currentLocoId || '').replace(/^0+/, '');
            if (cleanActLoco && cleanCurLoco && cleanActLoco === cleanCurLoco && !autoSelectedId) {
                opt.selected = true;
                autoSelectedId = act._id;
            }
            select.appendChild(opt);
        });

        selectGroup.style.display = 'block';
        statusText.innerHTML = "Choose a locomotive activity assignment from the dropdown below:";

        if (autoSelectedId) {
            onLocoSelected();
        }
    } catch (e) {
        statusText.innerHTML = `<span style="color:red;">Connection error during verification: ${e.message}</span>`;
    }
  }

  async function onLocoSelected() {
    const select = document.getElementById('wfms_loco_select');
    const activityId = select.value;
    const detailsDiv = document.getElementById('verification_details');
    const pushBtn = document.getElementById('pushBtn');
    const docSelectGroup = document.getElementById('docSelectGroup');
    const docSelect = document.getElementById('wfms_doc_select');

    if (!activityId) return;

    pushBtn.style.display = 'none';
    docSelectGroup.style.display = 'none';
    detailsDiv.innerHTML = `<span class="loader"></span> Resolving document slot for QC Checklist...`;

    try {
        const selectedAct = assignedActivities.find(act => act._id === activityId);
        const locoNum = selectedAct ? selectedAct.loco.number : '';

        const detailsResponse = await fetch('wfms_proxy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `action=get_activity_details&token=${encodeURIComponent(wfmsToken)}&activityId=${encodeURIComponent(activityId)}`
        });
        const detailsResult = await detailsResponse.json();

        if (!detailsResult.status || !detailsResult.data) {
            detailsDiv.innerHTML = `<span style="color:red;">Error fetching activity details: ${detailsResult.message || 'Unknown error'}</span>`;
            return;
        }

        const activityDetails = detailsResult.data;
        const qcFiles = activityDetails.qcFiles || [];

        if (qcFiles.length === 0) {
            detailsDiv.innerHTML = `<span style="color:red;">Configuration Error: No QC document slots found in this activity.</span>`;
            return;
        }

        // Search for best matching QC checklist document slot
        let targetDoc = qcFiles.find(doc => 
            doc.name && doc.name.toLowerCase().includes("in-process qc checklist")
        ) || qcFiles.find(doc => 
            doc.name && doc.name.toLowerCase().includes("qc checklist")
        ) || qcFiles.find(doc => 
            doc.name && doc.name.toLowerCase().includes("checklist")
        );

        // Populate doc selector
        docSelect.innerHTML = '';
        qcFiles.forEach(doc => {
            const opt = document.createElement('option');
            opt.value = doc._id;
            opt.text = doc.name;
            if (targetDoc && doc._id === targetDoc._id) {
                opt.selected = true;
            }
            docSelect.appendChild(opt);
        });

        if (!targetDoc) {
            targetDoc = qcFiles[0];
        }

        targetActivityId = activityId;
        targetDocId = targetDoc ? targetDoc._id : null;

        if (qcFiles.length > 1) {
            docSelectGroup.style.display = 'block';
        }

        detailsDiv.innerHTML = `
            <div style="color:green; font-weight:bold; margin-bottom:10px;">Verification Successful!</div>
            <strong>Selected Loco:</strong> #${locoNum}<br>
            <strong>Activity:</strong> ${selectedAct ? selectedAct.name : ''}<br>
            <strong>Document Slot:</strong> ${targetDoc ? targetDoc.name : 'Selected Slot'}
        `;
        pushBtn.style.display = 'inline-block';
    } catch (e) {
        detailsDiv.innerHTML = `<span style="color:red;">Verification error: ${e.message}</span>`;
    }
  }

  function onDocSelected() {
    const docSelect = document.getElementById('wfms_doc_select');
    targetDocId = docSelect.value;
  }

  async function doFinalPush() {
    const detailsDiv = document.getElementById('verification_details');
    const pushBtn = document.getElementById('pushBtn');
    
    pushBtn.disabled = true;
    pushBtn.innerHTML = '<span class="loader"></span> Uploading...';
    detailsDiv.innerHTML = `<span class="loader"></span> Uploading report to Loco WFMS...`;

    try {
        const formData = new FormData();
        formData.append('reportId', currentReportId);
        formData.append('activityId', targetActivityId);
        formData.append('docId', targetDocId);
        formData.append('wfms_token', wfmsToken);
        formData.append('is_hhp', '1');

        const uploadResponse = await fetch('upload-to-wfms', {
            method: 'POST',
            body: formData
        });
        const uploadResult = await uploadResponse.json();

        if (uploadResult.success) {
            detailsDiv.innerHTML = `<span style="color:green; font-weight:bold;">Success: ${uploadResult.message}</span>`;
            setTimeout(() => {
                alert("Success: " + uploadResult.message);
                location.reload();
            }, 1000);
        } else {
            detailsDiv.innerHTML = `<span style="color:red;">Upload failed: ${uploadResult.message}</span>`;
            pushBtn.disabled = false;
            pushBtn.innerText = "Push Report";
        }
    } catch (e) {
        detailsDiv.innerHTML = `<span style="color:red;">Upload error: ${e.message}</span>`;
        pushBtn.disabled = false;
        pushBtn.innerText = "Push Report";
    }
  }
</script>

</body>
</html>
"""

@viewHhpReports_bp.route('/viewHhpReports', methods=['GET', 'POST'])
def viewHhpReports():
    username = session.get('username') or request.args.get('username') or request.args.get('user_id')
    if not username:
        return '<script>alert("Unauthorized access. Please log in."); window.location.href="login.html";</script>', 401

    employee_name = session.get('employee_name', 'Unknown Employee')
    role = session.get('role', 'user')

    conn = None
    try:
        conn = get_hhp_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        # Ensure report table exists in hhp_loco_info with last_uploaded_hash
        cursor.execute("""CREATE TABLE IF NOT EXISTS `report` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` VARCHAR(100) NOT NULL,
            `file_name` VARCHAR(255) NOT NULL,
            `upload_date` DATETIME NOT NULL,
            `last_uploaded_hash` VARCHAR(64) DEFAULT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")

        try:
            cursor.execute("ALTER TABLE `report` ADD COLUMN `last_uploaded_hash` VARCHAR(64) DEFAULT NULL")
        except Exception:
            pass

        # Look up user from master loginpage to accurately determine role & employee name
        try:
            auth_conn = get_connection()
            auth_cur = auth_conn.cursor(dictionary=True, buffered=True)
            auth_cur.execute("SELECT username, employee_name, role FROM loginpage WHERE username = %s", (username,))
            u = auth_cur.fetchone()
            if u:
                employee_name = u.get('employee_name') or employee_name
                role = u.get('role') or role
                session['username'] = username
                session['employee_name'] = employee_name
                session['role'] = role
            auth_cur.close()
            auth_conn.close()
        except Exception:
            pass

        if request.args.get('role'):
            role = request.args.get('role')

        if role == 'admin':
            sql = "SELECT id, file_name, upload_date, DATE_FORMAT(upload_date, '%H:%i') AS upload_time, user_id FROM report ORDER BY upload_date DESC"
            cursor.execute(sql)
        else:
            sql = "SELECT id, file_name, upload_date, DATE_FORMAT(upload_date, '%H:%i') AS upload_time, user_id FROM report WHERE user_id = %s ORDER BY upload_date DESC"
            cursor.execute(sql, (username,))

        raw_reports = cursor.fetchall()

        formatted_reports = []
        for r in raw_reports:
            file_name = r['file_name']
            m_loco = re.search(r'\d+', file_name)
            loco_id = m_loco.group(0) if m_loco else ''

            m_status = re.search(r'_Report_([^_]+)_Version[\w-]+\.(pdf)$', file_name, re.IGNORECASE)
            status_text = m_status.group(1).strip().lower() if m_status else ''

            if status_text == 'completed':
                status_label = '<span class="status-label completed">Completed</span>'
            else:
                status_label = '<span class="status-label not-completed">Not Completed</span>'

            upload_dt = r['upload_date']
            date_fmt = upload_dt.strftime('%d/%m/%y') if hasattr(upload_dt, 'strftime') else str(upload_dt)

            formatted_reports.append({
                'id': r['id'],
                'file_name': file_name,
                'upload_date_fmt': date_fmt,
                'upload_time': r['upload_time'],
                'user_id': r['user_id'],
                'loco_id': loco_id,
                'status_label': status_label
            })

        return render_template_string(VIEW_HHP_REPORTS_HTML, username=username, employee_name=employee_name, role=role, reports=formatted_reports)
    except Exception as e:
        return f"Error: {e}"
    finally:
        if conn and conn.is_connected():
            conn.close()
