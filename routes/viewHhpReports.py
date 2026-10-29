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

  function openWFMSLogin(event, reportId, locoId) {
    alert(`WFMS Integration for Loco ID: ${locoId}`);
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

        # Ensure report table exists in hhp_loco_info
        cursor.execute("""CREATE TABLE IF NOT EXISTS `report` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` VARCHAR(100) NOT NULL,
            `file_name` VARCHAR(255) NOT NULL,
            `upload_date` DATETIME NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")

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
