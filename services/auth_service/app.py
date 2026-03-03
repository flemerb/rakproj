from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.environ.get('DB_PATH', '/app/data/users.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        token TEXT
    )''')
    # Create default admin
    password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    conn.execute('''INSERT OR IGNORE INTO users (username, password_hash, role)
                    VALUES (?, ?, ?)''', ('admin', password_hash, 'admin'))
    conn.commit()
    conn.close()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'auth_service'})

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE username=? AND password_hash=?',
        (username, password_hash)
    ).fetchone()

    if not user:
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

    token = secrets.token_hex(32)
    conn.execute('UPDATE users SET token=? WHERE id=?', (token, user['id']))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'token': token, 'role': user['role']})

@app.route('/auth/verify', methods=['POST'])
def verify():
    data = request.get_json()
    token = data.get('token')

    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE token=?', (token,)).fetchone()
    conn.close()

    if not user:
        return jsonify({'status': 'error', 'message': 'Invalid token'}), 401

    return jsonify({'status': 'success', 'username': user['username'], 'role': user['role']})

@app.route('/admin/users', methods=['GET'])
def list_users():
    # Verify caller is admin
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    conn = get_db()
    caller = conn.execute('SELECT * FROM users WHERE token=?', (token,)).fetchone()
    if not caller or caller['role'] != 'admin':
        conn.close()
        return jsonify({'status': 'error', 'message': 'Forbidden'}), 403

    users = conn.execute('SELECT id, username, role FROM users').fetchall()
    conn.close()
    return jsonify({'status': 'success', 'users': [dict(u) for u in users]})

@app.route('/admin/users', methods=['POST'])
def create_user():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    conn = get_db()
    caller = conn.execute('SELECT * FROM users WHERE token=?', (token,)).fetchone()
    if not caller or caller['role'] != 'admin':
        conn.close()
        return jsonify({'status': 'error', 'message': 'Forbidden'}), 403

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')  # 'user' or 'admin'

    if role not in ('user', 'admin'):
        return jsonify({'status': 'error', 'message': 'Role must be user or admin'}), 400

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        conn.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                     (username, password_hash, role))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'status': 'error', 'message': 'Username already exists'}), 409
    finally:
        conn.close()

    return jsonify({'status': 'success', 'message': f'User {username} created with role {role}'})

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    conn = get_db()
    caller = conn.execute('SELECT * FROM users WHERE token=?', (token,)).fetchone()
    if not caller or caller['role'] != 'admin':
        conn.close()
        return jsonify({'status': 'error', 'message': 'Forbidden'}), 403

    conn.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'User deleted'})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5004, debug=True)
