import threading
import time
import glob
import subprocess
import json
import os
import re
from functools import wraps
from ping3 import ping
from flask import Flask, render_template, jsonify, request, session
import logging
import socket

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

APP_PASSWORD = os.environ.get('APP_PASSWORD', '')
if not APP_PASSWORD:
    print("WARNING: APP_PASSWORD not set — write routes are disabled")

ping_interval = 0.5
output_status = False
HOST = '127.0.0.1'
PORT = 7000
MFW_DIR = '/home/seeroot/mfw'
MFW_LOG_DIR = '/var/www/html/logs'
DEVICES_FILE = os.path.join(os.path.dirname(__file__), 'devices.json')

DEFAULTS = {
    "Router":     "10.5.32.1",
    "Google DNS": "8.8.8.8",
    "Iphone":     "10.5.33.222",
}

device_lock = threading.Lock()


def load_devices():
    if os.path.exists(DEVICES_FILE):
        try:
            with open(DEVICES_FILE) as f:
                saved = json.load(f)
            return {k: {"ip": v, "status": None, "last_online": None} for k, v in saved.items()}
        except Exception as e:
            print(f"devices.json load error: {e} — using defaults")
    return {k: {"ip": v, "status": None, "last_online": None} for k, v in DEFAULTS.items()}


def save_devices():
    with device_lock:
        with open(DEVICES_FILE, 'w') as f:
            json.dump({k: v["ip"] for k, v in device_list.items()}, f)


device_list = load_devices()


# --- Auth ---

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authed'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True, silent=True) or {}
    if APP_PASSWORD and data.get('password') == APP_PASSWORD:
        session['authed'] = True
        return jsonify({'ok': True})
    return jsonify({'error': 'Wrong password'}), 401


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})


@app.route('/api/auth')
def auth_status():
    return jsonify({'authed': bool(session.get('authed'))})


# --- Validation ---

def valid_ip(ip):
    m = re.match(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$', ip)
    return bool(m and all(0 <= int(g) <= 255 for g in m.groups()))


def valid_name(name):
    return bool(name and len(name) <= 50 and re.match(r'^[A-Za-z0-9 _\-]+$', name))


# --- Core ---

def send_mfw(msg):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(f"{msg}\r\n".encode())
            print(f"MFW: {msg}")
    except Exception as e:
        print(f"socket error: {e}")


def ping_device(device):
    try:
        response = ping(device["ip"], timeout=2)
        device["status"] = bool(response)
        if response:
            device["last_online"] = time.strftime("%d %b %Y %H:%M:%S")
    except Exception:
        device["status"] = False


def ping_device_list():
    global output_status
    prev = {}
    while True:
        for name, device in list(device_list.items()):
            ping_device(device)
            last = prev.get(name)
            if device["status"] != last and last is not None:
                send_mfw(f"{name} {'Online' if device['status'] else 'Offline'}")
            prev[name] = device["status"]
        output_status = all(d["status"] for d in device_list.values())
        time.sleep(ping_interval)


# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    return jsonify({'output_status': output_status, 'device_list': device_list})


@app.route('/api/devices', methods=['POST'])
@requires_auth
def add_device():
    data = request.get_json(force=True, silent=True) or {}
    name = data.get('name', '').strip()
    ip   = data.get('ip', '').strip()
    if not valid_name(name):
        return jsonify({'error': 'Invalid name (max 50 chars, letters/numbers/spaces/-/_)'}), 400
    if not valid_ip(ip):
        return jsonify({'error': 'Invalid IP address'}), 400
    with device_lock:
        device_list[name] = {"ip": ip, "status": None, "last_online": None}
    save_devices()
    return jsonify({'added': name})


@app.route('/api/devices/<name>', methods=['DELETE'])
@requires_auth
def remove_device(name):
    with device_lock:
        if name not in device_list:
            return jsonify({'error': 'not found'}), 404
        del device_list[name]
    save_devices()
    return jsonify({'removed': name})


@app.route('/api/mfw')
def get_mfw():
    proc = subprocess.run(['pgrep', '-f', 'MFRA'], capture_output=True)
    return jsonify({'mfra_running': proc.returncode == 0})


@app.route('/api/mfw-log')
def get_mfw_log():
    files = sorted(glob.glob(f'{MFW_LOG_DIR}/099-099-00*.htm'))
    if not files:
        return '<p>No logs found.</p>', 200, {'Content-Type': 'text/html'}
    try:
        with open(files[-1]) as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    except PermissionError:
        return '<p>Log permission denied — run: sudo chmod o+r /var/www/html/logs/*.htm</p>', 200, {'Content-Type': 'text/html'}


@app.route('/api/page', methods=['POST'])
@requires_auth
def send_page():
    data = request.get_json(force=True, silent=True) or {}
    msg = data.get('message', '').strip()[:100]
    if not msg:
        return jsonify({'error': 'message required'}), 400
    send_mfw(msg)
    return jsonify({'sent': msg})


if __name__ == '__main__':
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    threading.Thread(target=ping_device_list, daemon=True).start()
    print("Network Monitoring started — http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
