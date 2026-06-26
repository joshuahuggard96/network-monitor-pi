import threading
import time
import glob
import subprocess
import xml.etree.ElementTree as ET
from ping3 import ping
from flask import Flask, render_template, jsonify, request
import logging
import socket

app = Flask(__name__)

ping_interval = 0.5
output_status = False
HOST = '127.0.0.1'
PORT = 7000
MFW_DIR = '/home/seeroot/mfw'
MFW_LOG_DIR = '/var/www/html/logs'

device_list = {
    "Router":     {"ip": "10.5.32.1",   "status": None, "last_online": None},
    "Google DNS": {"ip": "8.8.8.8",     "status": None, "last_online": None},
    "Iphone":     {"ip": "10.5.33.222", "status": None, "last_online": None},
}


def send_mfw(msg):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(f"{msg}<cr>".encode())
            print(f"MFW: {msg}")
    except Exception as e:
        print(f"socket error: {e}")


def ping_device(device):
    response = ping(device["ip"], timeout=2)
    device["status"] = bool(response)
    if response:
        device["last_online"] = time.strftime("%d %b %Y %H:%M:%S")


def ping_device_list():
    global output_status
    # ponytail: None means "unset" — avoids false alerts on first startup
    prev = {name: None for name in device_list}
    while True:
        for name, device in device_list.items():
            ping_device(device)
            if device["status"] != prev[name] and prev[name] is not None:
                label = "Online" if device["status"] else "Offline"
                send_mfw(f"{name} {label}")
            prev[name] = device["status"]
        output_status = all(d["status"] for d in device_list.values())
        time.sleep(ping_interval)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    return jsonify({'output_status': output_status, 'device_list': device_list})


@app.route('/api/mfw')
def get_mfw():
    proc = subprocess.run(['pgrep', '-f', 'MFRA'], capture_output=True)
    pagers = []
    try:
        tree = ET.parse(f'{MFW_DIR}/integrator.xml')
        for entry in tree.findall('.//Agent[@type="Alerter_2"]//Parameter[@name="AlDirc"]/Entry'):
            pagers.append({
                'user': entry.get('User'),
                'addr': entry.get('Addr'),
                'msg':  entry.get('Mesg'),
            })
    except Exception:
        pass
    return jsonify({'mfra_running': proc.returncode == 0, 'pagers': pagers})


@app.route('/api/mfw-log')
def get_mfw_log():
    files = sorted(glob.glob(f'{MFW_LOG_DIR}/*.htm'))
    if not files:
        return '<p>No logs found.</p>', 200, {'Content-Type': 'text/html'}
    try:
        with open(files[-1]) as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    except PermissionError:
        return '<p>Log permission denied — run: sudo chmod o+r /var/www/html/logs/*.htm</p>', 200, {'Content-Type': 'text/html'}


@app.route('/api/page', methods=['POST'])
def send_page():
    msg = request.json.get('message', 'Test')
    send_mfw(msg)
    return jsonify({'sent': msg})


if __name__ == '__main__':
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    threading.Thread(target=ping_device_list, daemon=True).start()
    print("Network Monitoring started — http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
