import sys, os, uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, request, jsonify, session, redirect
from db import get_connection

login_bp = Blueprint('login', __name__)

# Unique per server process startup so stale browser session cookies from a
# prior server run require a fresh login.
SERVER_BOOT_ID = uuid.uuid4().hex


def is_authenticated():
    """Return True only when the current session belongs to this server run."""
    return bool(
        session.get('user_id')
        and session.get('username')
        and session.get('boot_id') == SERVER_BOOT_ID
    )


@login_bp.route('/login', methods=['POST'])
def login():
    try:
        username = (request.form.get('username') or '').strip()
        password = (request.form.get('password') or '').strip()

        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required!'})

        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT username, employee_name, password, role FROM loginpage WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and password == user['password']:
            session.clear()
            session['user_id'] = user['username']
            session['username'] = user['username']
            session['employee_name'] = user['employee_name']
            session['role'] = user['role']
            session['boot_id'] = SERVER_BOOT_ID

            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'user_id': session['user_id'],
                'role': session['role'],
                'employee_name': user['employee_name']
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {e}'})


@login_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    if request.method == 'POST':
        return jsonify({'success': True, 'message': 'Logged out successfully.'})
    return redirect('/login.html')


@login_bp.route('/auth-status', methods=['GET'])
def auth_status():
    if not is_authenticated():
        return jsonify({'authenticated': False})
    return jsonify({
        'authenticated': True,
        'user_id': session.get('user_id', ''),
        'username': session.get('username', ''),
        'employee_name': session.get('employee_name', ''),
        'role': session.get('role', ''),
    })
