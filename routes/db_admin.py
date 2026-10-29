import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import io, csv
from flask import Blueprint, request, render_template_string, redirect, url_for, flash, jsonify, Response
from db import get_connection
import config

db_admin_bp = Blueprint('db_admin', __name__, url_prefix='/db-admin')

# CSS styled to mirror Database Studio's familiar tree structure & clean interface
CSS_STYLES = """
* { box-sizing: border-box; }
body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f8f9fa; color: #212529; font-size: 13px; }
.app-header { background: #fff; border-bottom: 1px solid #dee2e6; padding: 10px 18px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.logo-title { font-size: 17px; font-weight: 700; color: #2c3e50; display: flex; align-items: center; gap: 8px; text-decoration: none; }
.logo-badge { background: #3498db; color: #fff; font-size: 10px; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; font-weight: 600; }
.layout-container { display: flex; height: calc(100vh - 51px); }

/* Database Studio-Style Tree Sidebar */
.sidebar { width: 280px; background: #fdfdfd; border-right: 1px solid #dee2e6; overflow-y: auto; padding: 10px 0; flex-shrink: 0; }
.sidebar-filter-box { padding: 4px 12px 10px 12px; border-bottom: 1px solid #edf2f7; }
.sidebar-filter-input { width: 100%; padding: 5px 8px; font-size: 11px; border: 1px solid #ced4da; border-radius: 3px; outline: none; }
.sidebar-filter-input:focus { border-color: #3498db; }
.sidebar-tree-root { list-style: none; padding: 6px 0; margin: 0; }
.tree-node-server { font-weight: 700; font-size: 12px; color: #495057; padding: 4px 12px; display: flex; align-items: center; gap: 6px; }
.tree-dbs { list-style: none; padding-left: 12px; margin: 4px 0 0 0; }
.tree-db-item { margin: 2px 0; }
.tree-db-header { display: flex; align-items: center; gap: 6px; padding: 4px 8px; border-radius: 3px; font-size: 12px; color: #2c3e50; font-weight: 600; text-decoration: none; user-select: none; }
.tree-db-header:hover { background: #e8f4fd; }
.tree-db-header.active { background: #ebf5fb; color: #2980b9; }
.tree-toggle-btn { display: inline-flex; align-items: center; justify-content: center; width: 13px; height: 13px; border: 1px solid #adb5bd; border-radius: 2px; font-size: 10px; line-height: 1; cursor: pointer; background: #fff; color: #495057; font-weight: bold; flex-shrink: 0; }
.tree-toggle-btn:hover { background: #f1f3f5; border-color: #6c757d; }
.tree-tables-list { list-style: none; padding-left: 18px; margin: 2px 0 6px 0; border-left: 1px dotted #ced4da; }
.tree-table-item { display: flex; align-items: center; justify-content: space-between; padding: 3px 6px; font-size: 11.5px; color: #495057; text-decoration: none; border-radius: 3px; margin: 1px 0; }
.tree-table-item:hover { background: #e2f0fb; color: #0056b3; }
.tree-table-item.active { background: #2980b9; color: #fff; font-weight: 600; }
.tree-table-item.active .tree-badge { background: rgba(255,255,255,0.25); color: #fff; }
.tree-table-name { display: flex; align-items: center; gap: 5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tree-badge { font-size: 9.5px; color: #6c757d; background: #e9ecef; padding: 1px 5px; border-radius: 8px; flex-shrink: 0; }

/* Main Content Area */
.main-content { flex: 1; overflow-y: auto; padding: 18px 24px; background: #fdfdfd; }
.nav-breadcrumbs { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #6c757d; margin-bottom: 12px; }
.nav-breadcrumbs a { color: #2980b9; text-decoration: none; }
.tabs-header { display: flex; border-bottom: 2px solid #dee2e6; margin-bottom: 16px; gap: 4px; flex-wrap: wrap; }
.tab-link { padding: 8px 16px; text-decoration: none; color: #495057; font-weight: 600; border-top-left-radius: 4px; border-top-right-radius: 4px; border: 1px solid transparent; border-bottom: none; display: flex; align-items: center; gap: 6px; font-size: 12px; }
.tab-link:hover { background: #f1f3f5; }
.tab-link.active { background: #fff; border-color: #dee2e6; border-bottom-color: #fff; margin-bottom: -2px; color: #2980b9; }

/* Data Tables */
.data-table { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #dee2e6; box-shadow: 0 1px 3px rgba(0,0,0,0.02); font-size: 12px; }
.data-table th { background: #f8f9fa; border-bottom: 2px solid #dee2e6; border-right: 1px solid #dee2e6; padding: 8px 10px; text-align: left; font-weight: 600; color: #495057; white-space: nowrap; }
.data-table td { padding: 7px 10px; border-bottom: 1px solid #dee2e6; border-right: 1px solid #dee2e6; vertical-align: middle; white-space: nowrap; }
.data-table tr:hover { background: #f8fbff; }

/* Buttons & Alerts */
.btn { display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; font-size: 11px; border-radius: 3px; border: 1px solid #ced4da; background: #fff; color: #495057; text-decoration: none; cursor: pointer; transition: all 0.15s; }
.btn:hover { background: #f1f3f5; color: #212529; }
.btn-primary { background: #2980b9; border-color: #2980b9; color: #fff; }
.btn-primary:hover { background: #2471a3; color: #fff; }
.btn-danger { color: #e74c3c; border-color: #fadbd8; }
.btn-danger:hover { background: #e74c3c; color: #fff; }
.btn-sm { padding: 2px 6px; font-size: 11px; }
.action-group { display: flex; gap: 4px; flex-wrap: wrap; }
.alert { padding: 10px 14px; border-radius: 4px; margin-bottom: 14px; font-size: 12px; }
.alert-success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
.alert-danger { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
.alert-warning { background: #fff3cd; border: 1px solid #ffeeba; color: #856404; }

/* Database Studio-style Query Notice */
.query-box-success { background: #e8f8f5; border: 1px solid #a3e4d7; color: #117a65; padding: 8px 12px; border-radius: 4px; margin-bottom: 10px; font-size: 12px; display: flex; align-items: center; gap: 8px; }
.query-sql-display { background: #f8f9fa; border: 1px solid #dee2e6; border-left: 4px solid #2980b9; padding: 8px 12px; font-family: monospace; font-size: 12px; color: #2c3e50; margin-bottom: 14px; }
.sql-box { width: 100%; height: 120px; font-family: monospace; font-size: 13px; padding: 10px; border: 1px solid #ced4da; border-radius: 4px; margin-bottom: 10px; }
.form-card { background: #fff; border: 1px solid #dee2e6; border-radius: 4px; padding: 20px; max-width: 750px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-weight: 600; margin-bottom: 4px; color: #495057; font-size: 12px; }
.form-control { width: 100%; padding: 7px 10px; border: 1px solid #ced4da; border-radius: 4px; font-size: 12px; }
.pagination { display: flex; gap: 4px; margin-top: 14px; align-items: center; font-size: 12px; flex-wrap: wrap; }
.pagination a, .pagination span { padding: 4px 10px; border: 1px solid #dee2e6; background: #fff; text-decoration: none; color: #2980b9; border-radius: 3px; }
.pagination .current { background: #2980b9; color: #fff; border-color: #2980b9; }
"""

# HTML Layout Template with Expandable Tree Sidebar
BASE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title or "Database Studio" }} - loco_info</title>
    <style>{{ css | safe }}</style>
    <script>
        function toggleTree(dbName) {
            var el = document.getElementById('tree-sub-' + dbName);
            var btn = document.getElementById('tree-btn-' + dbName);
            if (!el) return;
            if (el.style.display === 'none') {
                el.style.display = 'block';
                if (btn) btn.innerHTML = '&minus;';
            } else {
                el.style.display = 'none';
                if (btn) btn.innerHTML = '&plus;';
            }
        }
        function filterSidebarTables(keyword) {
            keyword = keyword.toLowerCase().trim();
            var items = document.querySelectorAll('.tree-table-item');
            items.forEach(function(item) {
                var name = item.getAttribute('data-table-name') || '';
                if (!keyword || name.toLowerCase().indexOf(keyword) > -1) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        }
    </script>
</head>
<body>
    <header class="app-header">
        <a href="/db-admin" class="logo-title">
            <span>&#128451; Loco QC Database Studio</span>
            <span class="logo-badge">Pure Python</span>
        </a>
        <div style="font-size: 12px; color: #6c757d; display: flex; gap: 15px; align-items: center;">
            <span>Server: <strong>127.0.0.1:3306</strong></span>
            <span>Database: <strong>loco_info</strong></span>
            <a href="/" class="btn btn-sm" target="_blank">&#127968; Open Loco QC App</a>
        </div>
    </header>

    <div class="layout-container">
        <!-- Database Studio-Style Expandable Tree Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-filter-box">
                <input type="text" class="sidebar-filter-input" placeholder="Filter tables..." onkeyup="filterSidebarTables(this.value)">
            </div>
            
            <ul class="sidebar-tree-root">
                <li class="tree-node-server">
                    <span>&#128451; 127.0.0.1:3306</span>
                </li>
                
                <li style="padding: 0 8px;">
                    <ul class="tree-dbs">
                        {% for db in all_databases %}
                            {% set is_active_db = (db == current_db) %}
                            <li class="tree-db-item">
                                <div class="tree-db-header {% if is_active_db and not active_table %}active{% endif %}">
                                    <span class="tree-toggle-btn" id="tree-btn-{{ db }}" onclick="toggleTree('{{ db }}')">
                                        {% if is_active_db %}&minus;{% else %}&plus;{% endif %}
                                    </span>
                                    <a href="/db-admin" style="color: inherit; text-decoration: none; display: flex; align-items: center; gap: 5px;">
                                        <span>&#128193;</span>
                                        <span>{{ db }}</span>
                                    </a>
                                </div>
                                
                                {% if is_active_db %}
                                    <!-- Tables inside active database -->
                                    <ul class="tree-tables-list" id="tree-sub-{{ db }}">
                                        {% for tbl in tables %}
                                            <li>
                                                <a href="/db-admin/browse/{{ tbl.Name }}" class="tree-table-item {% if active_table == tbl.Name %}active{% endif %}" data-table-name="{{ tbl.Name }}" title="{{ tbl.Name }} ({{ tbl.Rows }} rows)">
                                                    <span class="tree-table-name">
                                                        <span>&#128203;</span>
                                                        <span>{{ tbl.Name }}</span>
                                                    </span>
                                                    <span class="tree-badge">{{ tbl.Rows }}</span>
                                                </a>
                                            </li>
                                        {% endfor %}
                                    </ul>
                                {% else %}
                                    <!-- Collapsed sibling database -->
                                    <ul class="tree-tables-list" id="tree-sub-{{ db }}" style="display: none;">
                                        <li style="padding: 4px 6px; color: #888; font-size: 11px;">
                                            <a href="/db-admin" style="color: #2980b9; text-decoration: none;">Click to view {{ db }}</a>
                                        </li>
                                    </ul>
                                {% endif %}
                            </li>
                        {% endfor %}
                    </ul>
                </li>
            </ul>
        </aside>

        <!-- Main Content Area -->
        <main class="main-content">
            <div class="nav-breadcrumbs">
                <a href="/db-admin">&#128451; 127.0.0.1:3306</a> &gt;
                <a href="/db-admin"><strong>loco_info</strong></a>
                {% if active_table %}
                    &gt; <strong style="color: #212529;">{{ active_table }}</strong>
                {% endif %}
            </div>

            {% if msg or request.args.get('msg') %}
                <div class="alert alert-{{ msg_type or request.args.get('msg_type') or 'success' }}">{{ msg or request.args.get('msg') }}</div>
            {% endif %}

            <!-- Top Nav Tabs (Mirrors Database Studio tabs) -->
            <div class="tabs-header">
                <a href="/db-admin" class="tab-link {% if active_tab == 'structure_db' %}active{% endif %}">&#128450; Database Structure</a>
                {% if active_table %}
                    <a href="/db-admin/browse/{{ active_table }}" class="tab-link {% if active_tab == 'browse' %}active{% endif %}">&#128065; Browse Data</a>
                    <a href="/db-admin/structure/{{ active_table }}" class="tab-link {% if active_tab == 'structure_table' %}active{% endif %}">&#128295; Table Structure</a>
                    <a href="/db-admin/insert/{{ active_table }}" class="tab-link {% if active_tab == 'insert' %}active{% endif %}">&#10133; Insert Row</a>
                    <a href="/db-admin/export/{{ active_table }}" class="tab-link">&#128229; Export Table</a>
                {% endif %}
                <a href="/db-admin/sql" class="tab-link {% if active_tab == 'sql' %}active{% endif %}">&#9881; SQL Query Console</a>
                <a href="/db-admin/export-all" class="tab-link">&#128190; Export Full Database (SQL)</a>
            </div>

            <!-- Content Slot -->
            {{ content | safe }}
        </main>
    </div>
</body>
</html>
"""


def get_all_databases():
    """Helper to fetch all databases on the MySQL server."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        dbs = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        # Sort so loco_info appears prominently, system dbs at the bottom
        priority = ['loco_info', 'hhp_loco_info', 'station_info', 'test']
        sorted_dbs = []
        for p in priority:
            if p in dbs:
                sorted_dbs.append(p)
        for d in sorted(dbs):
            if d not in sorted_dbs:
                sorted_dbs.append(d)
        return sorted_dbs
    except Exception:
        return ['loco_info', 'hhp_loco_info', 'station_info', 'test', 'mysql', 'information_schema', 'performance_schema']


def get_all_tables_info(db_name="loco_info"):
    """Helper to fetch all tables with stats like Database Studio."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SHOW TABLE STATUS FROM `{db_name}`")
        tables = cursor.fetchall()
        cursor.close()
        conn.close()
        return tables, None
    except Exception as e:
        return [], str(e)


def get_primary_key_for_table(cursor, table_name):
    """Detects primary key or fallback identifier column."""
    try:
        cursor.execute(f"SHOW KEYS FROM `{table_name}` WHERE Key_name = 'PRIMARY'")
        pk_row = cursor.fetchone()
        if pk_row and pk_row.get('Column_name'):
            return pk_row['Column_name']
    except Exception:
        pass

    try:
        cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
        all_cols = [c['Field'] for c in cursor.fetchall()]
        for candidate in ['sno', 'id', 'report_id', 'loco_no', 'user_id', 'sl_no']:
            if candidate in all_cols:
                return candidate
        return all_cols[0] if all_cols else None
    except Exception:
        return None


def format_bytes(size):
    """Format bytes into KB / MB."""
    if not size:
        return "0 KB"
    kb = size / 1024.0
    if kb >= 1024:
        return f"{kb / 1024.0:.1f} MB"
    return f"{kb:.1f} KB"


# 1. Structure View of Entire Database (Mirrors Database Studio structure)
@db_admin_bp.route('/', strict_slashes=False)
def db_structure():
    all_dbs = get_all_databases()
    tables, conn_err = get_all_tables_info()
    total_rows = sum([t.get('Rows') or 0 for t in tables])
    total_size = sum([(t.get('Data_length') or 0) + (t.get('Index_length') or 0) for t in tables])

    err_banner = ""
    if conn_err:
        err_banner = f"""
        <div class="alert alert-danger">
            <strong>Database Connection Error:</strong> Unable to connect to MySQL database <code>loco_info</code> on port 3306.<br>
            <em>Details: {conn_err}</em><br>
            Please ensure MySQL server is running.
        </div>
        """

    content = f"""
    {err_banner}
    <div style="background: #fff; padding: 15px; border: 1px solid #dee2e6; border-radius: 4px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div>
            <h3 style="margin: 0 0 4px 0; color: #2c3e50;">Database: loco_info</h3>
            <span style="color: #6c757d; font-size: 12px;">Total Tables: <strong>{len(tables)}</strong> | Total Records: <strong>{total_rows:,}</strong> | Total Size: <strong>{format_bytes(total_size)}</strong></span>
        </div>
        <div style="display: flex; gap: 8px;">
            <a href="/db-admin/sql" class="btn btn-primary">&#9881; Run SQL Query</a>
            <a href="/db-admin/export-all" class="btn">&#128190; Export .SQL Dump</a>
        </div>
    </div>

    <table class="data-table">
        <thead>
            <tr>
                <th style="width: 25px;"><input type="checkbox"></th>
                <th>Table Name</th>
                <th style="width: 380px;">Action</th>
                <th style="text-align: right;">Rows</th>
                <th>Engine</th>
                <th>Collation</th>
                <th style="text-align: right;">Size</th>
            </tr>
        </thead>
        <tbody>
    """
    for t in tables:
        name = t.get('Name')
        rows = t.get('Rows') or 0
        engine = t.get('Engine') or 'InnoDB'
        collation = t.get('Collation') or 'utf8mb4_unicode_ci'
        size = format_bytes((t.get('Data_length') or 0) + (t.get('Index_length') or 0))

        content += f"""
            <tr>
                <td><input type="checkbox"></td>
                <td><a href="/db-admin/browse/{name}" style="font-weight: 600; color: #2980b9; text-decoration: none;">&#128203; {name}</a></td>
                <td>
                    <div class="action-group">
                        <a href="/db-admin/browse/{name}" class="btn btn-sm">&#128065; Browse</a>
                        <a href="/db-admin/structure/{name}" class="btn btn-sm">&#128295; Structure</a>
                        <a href="/db-admin/insert/{name}" class="btn btn-sm">&#10133; Insert</a>
                        <a href="/db-admin/export/{name}" class="btn btn-sm">&#128229; Export</a>
                        <a href="/db-admin/empty/{name}" class="btn btn-sm btn-danger" onclick="return confirm('Empty table {name}? All rows will be permanently deleted.');">&#128465; Empty</a>
                        <a href="/db-admin/drop/{name}" class="btn btn-sm btn-danger" onclick="return confirm('DROP TABLE {name} permanently?');">&#10060; Drop</a>
                    </div>
                </td>
                <td style="text-align: right; font-weight: 600;">{rows:,}</td>
                <td><span style="background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{engine}</span></td>
                <td style="color: #6c757d; font-size: 11px;">{collation}</td>
                <td style="text-align: right; color: #6c757d;">{size}</td>
            </tr>
        """

    content += f"""
        </tbody>
        <tfoot>
            <tr style="background: #f8f9fa; font-weight: bold;">
                <td></td>
                <td>{len(tables)} tables</td>
                <td></td>
                <td style="text-align: right;">{total_rows:,}</td>
                <td></td>
                <td></td>
                <td style="text-align: right;">{format_bytes(total_size)}</td>
            </tr>
        </tfoot>
    </table>
    """

    return render_template_string(
        BASE_TEMPLATE,
        title="Database Structure",
        css=CSS_STYLES,
        all_databases=all_dbs,
        current_db="loco_info",
        tables=tables,
        active_table=None,
        active_tab="structure_db",
        content=content
    )


# 2. Browse Table Data View (View, Edit, Delete, Copy rows!)
@db_admin_bp.route('/browse/<table_name>')
def browse_table(table_name):
    all_dbs = get_all_databases()
    tables, _ = get_all_tables_info()
    page = int(request.args.get('page', 1))
    search_query = request.args.get('q', '').strip()
    per_page = 50
    offset = (page - 1) * per_page

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        primary_key = get_primary_key_for_table(cursor, table_name)

        # Get columns
        cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
        columns = [c['Field'] for c in cursor.fetchall()]

        # Filter query if searched
        where_clause = ""
        params = []
        if search_query and columns:
            conds = [f"`{c}` LIKE %s" for c in columns]
            where_clause = " WHERE " + " OR ".join(conds)
            params = [f"%{search_query}%"] * len(columns)

        # Total count
        cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`{where_clause}", tuple(params))
        total_count = cursor.fetchone()['count']

        # Fetch rows
        query_sql = f"SELECT * FROM `{table_name}`{where_clause} LIMIT %s OFFSET %s"
        cursor.execute(query_sql, tuple(params + [per_page, offset]))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
    except Exception as e:
        return render_template_string(
            BASE_TEMPLATE,
            title=f"Browse {table_name}",
            css=CSS_STYLES,
            all_databases=all_dbs,
            current_db="loco_info",
            tables=tables,
            active_table=table_name,
            active_tab="browse",
            content=f"<div class='alert alert-danger'>Error loading table <code>{table_name}</code>: {str(e)}</div>"
        )

    total_pages = max(1, (total_count + per_page - 1) // per_page)
    clear_btn = f'<a href="/db-admin/browse/{table_name}" class="btn">Clear</a>' if search_query else ''

    content = f"""
    <!-- Database Studio-style Query Notice -->
    <div class="query-box-success">
        <span style="font-size: 14px; font-weight: bold;">&#10004;</span>
        <span>Showing rows {offset + 1 if total_count > 0 else 0} - {min(offset + len(rows), total_count)} ({total_count:,} total)</span>
    </div>
    
    <div class="query-sql-display">
        <strong>SELECT</strong> * <strong>FROM</strong> `loco_info`.`{table_name}`{where_clause} <strong>LIMIT</strong> {offset}, {per_page};
    </div>

    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
        <div>
            <h3 style="margin: 0; color: #2c3e50;">Table: {table_name}</h3>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <form method="GET" action="/db-admin/browse/{table_name}" style="display: flex; gap: 4px; margin: 0;">
                <input type="text" name="q" value="{search_query}" placeholder="Search table..." class="form-control" style="width: 180px; padding: 4px 8px; font-size: 11px;">
                <button type="submit" class="btn">&#128269; Search</button>
                {clear_btn}
            </form>
            <a href="/db-admin/insert/{table_name}" class="btn btn-primary">&#10133; Insert New Row</a>
            <a href="/db-admin/export/{table_name}" class="btn">&#128229; Export (CSV)</a>
        </div>
    </div>

    <div style="overflow-x: auto; background: #fff; border: 1px solid #dee2e6; border-radius: 4px;">
        <table class="data-table">
            <thead>
                <tr>
                    <th style="width: 140px; text-align: center;">Actions</th>
    """
    for col in columns:
        is_pk = (col == primary_key)
        content += f"<th>{col} {'&#128273;' if is_pk else ''}</th>"
    content += "</tr></thead><tbody>"

    if not rows:
        content += f"<tr><td colspan='{len(columns) + 1}' style='text-align: center; padding: 25px; color: #888;'>No records found in table.</td></tr>"

    for r in rows:
        pk_val = r.get(primary_key) if primary_key else None
        content += "<tr><td style='text-align: center;'><div class='action-group' style='justify-content: center;'>"
        if primary_key and pk_val is not None:
            content += f"""
                <a href="/db-admin/edit/{table_name}?pk={pk_val}&pk_col={primary_key}" class="btn btn-sm" title="Edit row">&#9998; Edit</a>
                <a href="/db-admin/copy/{table_name}?pk={pk_val}&pk_col={primary_key}" class="btn btn-sm" title="Copy row">&#128203; Copy</a>
                <a href="/db-admin/delete-row/{table_name}?pk={pk_val}&pk_col={primary_key}" class="btn btn-sm btn-danger" onclick="return confirm('Delete this row?');" title="Delete row">&#128465; Delete</a>
            """
        else:
            content += "<span style='color: #aaa;'>N/A</span>"
        content += "</div></td>"

        for col in columns:
            val = r.get(col)
            val_str = "" if val is None else str(val)
            if len(val_str) > 60:
                val_str = val_str[:60] + "..."
            content += f"<td>{val_str}</td>"
        content += "</tr>"

    content += "</tbody></table></div>"

    # Pagination
    if total_pages > 1:
        content += "<div class='pagination'>"
        q_param = f"&q={search_query}" if search_query else ""
        if page > 1:
            content += f"<a href='/db-admin/browse/{table_name}?page={page - 1}{q_param}'>&laquo; Prev</a>"
        for p in range(max(1, page - 4), min(total_pages + 1, page + 5)):
            if p == page:
                content += f"<span class='current'>{p}</span>"
            else:
                content += f"<a href='/db-admin/browse/{table_name}?page={p}{q_param}'>{p}</a>"
        if page < total_pages:
            content += f"<a href='/db-admin/browse/{table_name}?page={page + 1}{q_param}'>Next &raquo;</a>"
        content += "</div>"

    return render_template_string(
        BASE_TEMPLATE,
        title=f"Browse {table_name}",
        css=CSS_STYLES,
        all_databases=all_dbs,
        current_db="loco_info",
        tables=tables,
        active_table=table_name,
        active_tab="browse",
        content=content
    )


# 3. Table Column Structure View
@db_admin_bp.route('/structure/<table_name>')
def table_structure(table_name):
    all_dbs = get_all_databases()
    tables, _ = get_all_tables_info()
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")
        columns = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        return render_template_string(
            BASE_TEMPLATE,
            title=f"Structure {table_name}",
            css=CSS_STYLES,
            all_databases=all_dbs,
            current_db="loco_info",
            tables=tables,
            active_table=table_name,
            active_tab="structure_table",
            content=f"<div class='alert alert-danger'>Error loading table structure: {str(e)}</div>"
        )

    content = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <h3 style="margin: 0; color: #2c3e50;">Columns Structure: {table_name}</h3>
        <a href="/db-admin/browse/{table_name}" class="btn btn-primary">&#128065; Browse Data</a>
    </div>

    <table class="data-table">
        <thead>
            <tr>
                <th>#</th>
                <th>Column Name</th>
                <th>Type</th>
                <th>Collation</th>
                <th>Null</th>
                <th>Key</th>
                <th>Default</th>
                <th>Extra</th>
            </tr>
        </thead>
        <tbody>
    """
    for idx, col in enumerate(columns):
        is_pk = col.get('Key') == 'PRI'
        content += f"""
            <tr {'style="background: #fff8e1;"' if is_pk else ''}>
                <td>{idx + 1}</td>
                <td><strong>{col.get('Field')}</strong> {'&#128273;' if is_pk else ''}</td>
                <td><code>{col.get('Type')}</code></td>
                <td>{col.get('Collation') or ''}</td>
                <td>{col.get('Null')}</td>
                <td><strong>{col.get('Key')}</strong></td>
                <td>{col.get('Default') or '<em>NULL</em>'}</td>
                <td>{col.get('Extra') or ''}</td>
            </tr>
        """
    content += "</tbody></table>"

    return render_template_string(
        BASE_TEMPLATE,
        title=f"Structure {table_name}",
        css=CSS_STYLES,
        all_databases=all_dbs,
        current_db="loco_info",
        tables=tables,
        active_table=table_name,
        active_tab="structure_table",
        content=content
    )


# 4. Insert New Row
@db_admin_bp.route('/insert/<table_name>', methods=['GET', 'POST'])
def insert_row(table_name):
    all_dbs = get_all_databases()
    tables, _ = get_all_tables_info()
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")
        columns = cursor.fetchall()

        if request.method == 'POST':
            insert_cols = []
            insert_vals = []
            for col in columns:
                field = col['Field']
                if col.get('Extra') == 'auto_increment':
                    continue
                val = request.form.get(field)
                if val is not None and val != "":
                    insert_cols.append(f"`{field}`")
                    insert_vals.append(val)

            if insert_cols:
                placeholders = ", ".join(["%s"] * len(insert_vals))
                cols_sql = ", ".join(insert_cols)
                cursor.execute(f"INSERT INTO `{table_name}` ({cols_sql}) VALUES ({placeholders})", tuple(insert_vals))
                conn.commit()

            cursor.close()
            conn.close()
            return redirect(f"/db-admin/browse/{table_name}?msg=Row+inserted+successfully&msg_type=success")

        cursor.close()
        conn.close()
    except Exception as e:
        return render_template_string(
            BASE_TEMPLATE,
            title=f"Insert into {table_name}",
            css=CSS_STYLES,
            all_databases=all_dbs,
            current_db="loco_info",
            tables=tables,
            active_table=table_name,
            active_tab="insert",
            content=f"<div class='alert alert-danger'>Error inserting row: {str(e)}</div>"
        )

    content = f"""
    <div class="form-card">
        <h3 style="margin-top: 0; color: #2c3e50;">Insert New Row into <code>{table_name}</code></h3>
        <form method="POST">
    """
    for col in columns:
        field = col['Field']
        ctype = col['Type']
        is_ai = col.get('Extra') == 'auto_increment'
        content += f"""
            <div class="form-group">
                <label>{field} <span style="font-weight: normal; color: #888;">({ctype})</span> {'[Auto Increment]' if is_ai else ''}</label>
                <input type="text" name="{field}" class="form-control" {'disabled placeholder="(Auto Generated)"' if is_ai else ''}>
            </div>
        """
    content += """
            <div style="margin-top: 15px;">
                <button type="submit" class="btn btn-primary">&#10004; Insert Row</button>
                <a href="javascript:history.back()" class="btn">Cancel</a>
            </div>
        </form>
    </div>
    """

    return render_template_string(
        BASE_TEMPLATE,
        title=f"Insert into {table_name}",
        css=CSS_STYLES,
        all_databases=all_dbs,
        current_db="loco_info",
        tables=tables,
        active_table=table_name,
        active_tab="insert",
        content=content
    )


# 5. Edit Existing Row
@db_admin_bp.route('/edit/<table_name>', methods=['GET', 'POST'])
def edit_row(table_name):
    all_dbs = get_all_databases()
    tables, _ = get_all_tables_info()
    pk_val = request.args.get('pk')
    pk_col_override = request.args.get('pk_col')

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        pk_col = pk_col_override or get_primary_key_for_table(cursor, table_name)

        cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")
        columns = cursor.fetchall()

        if request.method == 'POST':
            update_clauses = []
            update_vals = []
            for col in columns:
                field = col['Field']
                if field == pk_col:
                    continue
                val = request.form.get(field)
                update_clauses.append(f"`{field}` = %s")
                update_vals.append(val if val != "" else None)

            update_vals.append(pk_val)
            sql = f"UPDATE `{table_name}` SET {', '.join(update_clauses)} WHERE `{pk_col}` = %s"
            cursor.execute(sql, tuple(update_vals))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(f"/db-admin/browse/{table_name}?msg=Row+updated+successfully&msg_type=success")

        cursor.execute(f"SELECT * FROM `{table_name}` WHERE `{pk_col}` = %s", (pk_val,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        return render_template_string(
            BASE_TEMPLATE,
            title=f"Edit {table_name}",
            css=CSS_STYLES,
            all_databases=all_dbs,
            current_db="loco_info",
            tables=tables,
            active_table=table_name,
            active_tab="browse",
            content=f"<div class='alert alert-danger'>Error editing row: {str(e)}</div>"
        )

    content = f"""
    <div class="form-card">
        <h3 style="margin-top: 0; color: #2c3e50;">Edit Row in <code>{table_name}</code> ({pk_col} = {pk_val})</h3>
        <form method="POST">
    """
    for col in columns:
        field = col['Field']
        ctype = col['Type']
        is_pk = (field == pk_col)
        current_val = row.get(field) if row else ""
        content += f"""
            <div class="form-group">
                <label>{field} <span style="font-weight: normal; color: #888;">({ctype})</span> {'[Primary Key]' if is_pk else ''}</label>
                <input type="text" name="{field}" value="{"" if current_val is None else current_val}" class="form-control" {'readonly style="background: #f1f3f5;"' if is_pk else ''}>
            </div>
        """
    content += """
            <div style="margin-top: 15px;">
                <button type="submit" class="btn btn-primary">&#128190; Save Changes</button>
                <a href="javascript:history.back()" class="btn">Cancel</a>
            </div>
        </form>
    </div>
    """

    return render_template_string(
        BASE_TEMPLATE,
        title=f"Edit {table_name}",
        css=CSS_STYLES,
        all_databases=all_dbs,
        current_db="loco_info",
        tables=tables,
        active_table=table_name,
        active_tab="browse",
        content=content
    )


# 6. Delete Row
@db_admin_bp.route('/delete-row/<table_name>')
def delete_row(table_name):
    pk_val = request.args.get('pk')
    pk_col_override = request.args.get('pk_col')
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        pk_col = pk_col_override or get_primary_key_for_table(cursor, table_name)
        cursor.execute(f"DELETE FROM `{table_name}` WHERE `{pk_col}` = %s", (pk_val,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(f"/db-admin/browse/{table_name}?msg=Row+deleted+successfully&msg_type=success")
    except Exception as e:
        return redirect(f"/db-admin/browse/{table_name}?msg=Error+deleting+row:+{str(e)}&msg_type=danger")


# 7. Copy / Duplicate Row
@db_admin_bp.route('/copy/<table_name>')
def copy_row(table_name):
    pk_val = request.args.get('pk')
    pk_col_override = request.args.get('pk_col')
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        pk_col = pk_col_override or get_primary_key_for_table(cursor, table_name)

        cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")
        columns = [c['Field'] for c in cursor.fetchall() if c['Field'] != pk_col and c.get('Extra') != 'auto_increment']

        cols_sql = ", ".join([f"`{c}`" for c in columns])
        sql = f"INSERT INTO `{table_name}` ({cols_sql}) SELECT {cols_sql} FROM `{table_name}` WHERE `{pk_col}` = %s"
        cursor.execute(sql, (pk_val,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(f"/db-admin/browse/{table_name}?msg=Row+duplicated+successfully&msg_type=success")
    except Exception as e:
        return redirect(f"/db-admin/browse/{table_name}?msg=Error+copying+row:+{str(e)}&msg_type=danger")


# 8. Empty / Truncate Table
@db_admin_bp.route('/empty/<table_name>')
def empty_table(table_name):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute(f"TRUNCATE TABLE `{table_name}`")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(f"/db-admin?msg=Table+{table_name}+emptied+successfully&msg_type=success")
    except Exception as e:
        return redirect(f"/db-admin?msg=Error+emptying+table:+{str(e)}&msg_type=danger")


# 9. Drop Table
@db_admin_bp.route('/drop/<table_name>')
def drop_table(table_name):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute(f"DROP TABLE `{table_name}`")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(f"/db-admin?msg=Table+{table_name}+dropped+successfully&msg_type=success")
    except Exception as e:
        return redirect(f"/db-admin?msg=Error+dropping+table:+{str(e)}&msg_type=danger")


# 10. SQL Console (Execute queries)
@db_admin_bp.route('/sql', methods=['GET', 'POST'])
def sql_console():
    all_dbs = get_all_databases()
    tables, _ = get_all_tables_info()
    query = request.form.get('sql_query', 'SELECT * FROM loco LIMIT 20;') if request.method == 'POST' else 'SELECT * FROM loco LIMIT 20;'
    results = None
    columns = []
    error = None
    affected = None

    if request.method == 'POST' and query.strip():
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            if cursor.description:
                results = cursor.fetchall()
                columns = [d[0] for d in cursor.description]
            else:
                conn.commit()
                affected = cursor.rowcount
            cursor.close()
            conn.close()
        except Exception as e:
            error = str(e)

    content = f"""
    <div style="background: #fff; padding: 20px; border: 1px solid #dee2e6; border-radius: 4px; margin-bottom: 20px;">
        <h3 style="margin-top: 0; color: #2c3e50;">&#9881; SQL Query Console on <code>loco_info</code></h3>
        <form method="POST">
            <textarea name="sql_query" class="sql-box">{query}</textarea>
            <div>
                <button type="submit" class="btn btn-primary">&#9654; Execute Query</button>
            </div>
        </form>
    </div>
    """

    if error:
        content += f"<div class='alert alert-danger'><strong>SQL Error:</strong> {error}</div>"
    elif affected is not None:
        content += f"<div class='alert alert-success'>Query executed successfully. <strong>{affected}</strong> row(s) affected.</div>"
    elif results is not None:
        content += f"""
        <div style="margin-bottom: 10px; font-weight: bold; color: #2c3e50;">Returned {len(results)} row(s):</div>
        <div style="overflow-x: auto; background: #fff; border: 1px solid #dee2e6; border-radius: 4px;">
            <table class="data-table">
                <thead><tr>
        """
        for c in columns:
            content += f"<th>{c}</th>"
        content += "</tr></thead><tbody>"
        for r in results:
            content += "<tr>"
            for c in columns:
                content += f"<td>{r.get(c)}</td>"
            content += "</tr>"
        content += "</tbody></table></div>"

    return render_template_string(
        BASE_TEMPLATE,
        title="SQL Query Console",
        css=CSS_STYLES,
        all_databases=all_dbs,
        current_db="loco_info",
        tables=tables,
        active_table=None,
        active_tab="sql",
        content=content
    )


# 11. Export Table as CSV
@db_admin_bp.route('/export/<table_name>')
def export_table_csv(table_name):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `{table_name}`")
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description] if cursor.description else []
        cursor.close()
        conn.close()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        for r in rows:
            writer.writerow([r.get(c) for c in columns])

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={table_name}.csv"}
        )
    except Exception as e:
        return redirect(f"/db-admin/browse/{table_name}?msg=Export+error:+{str(e)}&msg_type=danger")


# 12. Export Full Database as .SQL Dump
@db_admin_bp.route('/export-all')
def export_database_sql():
    try:
        tables, _ = get_all_tables_info()
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql_dump = f"-- Loco QC Database Studio Dump\n-- Database: loco_info\n-- Host: 127.0.0.1\n\nSET FOREIGN_KEY_CHECKS=0;\n\n"

        for t in tables:
            tname = t['Name']
            # Create Table
            cursor.execute(f"SHOW CREATE TABLE `{tname}`")
            create_row = cursor.fetchone()
            sql_dump += f"-- Table structure for `{tname}`\nDROP TABLE IF EXISTS `{tname}`;\n"
            sql_dump += create_row.get('Create Table', '') + ";\n\n"

            # Rows
            cursor.execute(f"SELECT * FROM `{tname}`")
            rows = cursor.fetchall()
            if rows:
                cols = [f"`{d[0]}`" for d in cursor.description]
                cols_str = ", ".join(cols)
                sql_dump += f"-- Dumping data for `{tname}`\nINSERT INTO `{tname}` ({cols_str}) VALUES\n"
                val_lines = []
                for r in rows:
                    row_vals = []
                    for val in r.values():
                        if val is None:
                            row_vals.append("NULL")
                        elif isinstance(val, (int, float)):
                            row_vals.append(str(val))
                        else:
                            escaped = str(val).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")
                            row_vals.append(f"'{escaped}'")
                    val_lines.append(f"({', '.join(row_vals)})")
                sql_dump += ",\n".join(val_lines) + ";\n\n"

        sql_dump += "SET FOREIGN_KEY_CHECKS=1;\n"
        cursor.close()
        conn.close()

        return Response(
            sql_dump,
            mimetype="application/sql",
            headers={"Content-Disposition": "attachment;filename=loco_info_backup.sql"}
        )
    except Exception as e:
        return redirect(f"/db-admin?msg=Export+error:+{str(e)}&msg_type=danger")
