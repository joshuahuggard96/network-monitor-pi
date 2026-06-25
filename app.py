import threading
import time
from ping3 import ping
from flask import Flask, render_template, jsonify
import logging
import socket

app = Flask(__name__)

ping_interval = 0.5
output_status = False
HOST = '127.0.0.1'
PORT = 7000

device_list = {
    "Router":     {"ip": "10.5.32.1",   "status": None, "last_online": None},
    "Google DNS": {"ip": "8.8.8.8",     "status": None, "last_online": None},
    "Iphone":     {"ip": "10.5.33.222", "status": None, "last_online": None},
}


def ping_device(device):
    response = ping(device["ip"], timeout=2)
    device["status"] = bool(response)
    if response:
        device["last_online"] = time.strftime("%d %b %Y %H:%M:%S")


def ping_device_list():
    global output_status
    while True:
        all_online = all(d["status"] for d in device_list.values())
        for device in device_list.values():
            ping_device(device)
        output_status = all(d["status"] for d in device_list.values())
        Send_output(HOST, PORT)
        time.sleep(ping_interval)


def Send_output(h, p):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((h, p))
            s.sendall(f"{output_status}<cr>".encode())
    except Exception as e:
        print(f"socket error: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    return jsonify({'output_status': output_status, 'device_list': device_list})


if __name__ == '__main__':
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    threading.Thread(target=ping_device_list, daemon=True).start()
    print("Network Monitoring started — http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)
