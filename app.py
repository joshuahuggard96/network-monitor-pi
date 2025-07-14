import os
import json
import threading
import time
import subprocess
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None  # For development on non-Pi systems

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default = {
            "devices": [
                {"ip": "8.8.8.8", "name": "Google DNS", "relay": False, "offline_count": 0},
            ],
            "interval": 30,
            "relay_pin": 17,
            "offline_threshold": 3,
            "users": {
                "admin": generate_password_hash("admin")
            }
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default, f, indent=2)
        return default
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

config = load_config()
devices_status = {d["ip"]: {"online": None, "last_ping": None, "response": None, "offline_count": 0} for d in config["devices"]}

app = Flask(__name__)
app.secret_key = os.urandom(24)

def ping(ip):
    try:
        output = subprocess.check_output(["ping", "-c", "1", "-W", "1", ip], stderr=subprocess.STDOUT, universal_newlines=True)
        ms = None
        for line in output.splitlines():
            if "time=" in line:
                ms = float(line.split("time=")[1].split()[0])
        return True, ms
    except Exception:
        return False, None

def relay_on(pin):
    if GPIO:
        GPIO.output(pin, GPIO.HIGH)

def relay_off(pin):
    if GPIO:
        GPIO.output(pin, GPIO.LOW)

def setup_gpio(pin):
    if GPIO:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        relay_off(pin)

def monitor_devices():
    setup_gpio(config["relay_pin"])
    while True:
        for device in config["devices"]:
            ip = device["ip"]
            online, response = ping(ip)
            status = devices_status[ip]
            status["online"] = online
            status["last_ping"] = time.strftime("%Y-%m-%d %H:%M:%S")
            status["response"] = response
            if not online:
                status["offline_count"] += 1
            else:
                status["offline_count"] = 0

            # Relay logic
            if device.get("relay", False):
                if status["offline_count"] >= config["offline_threshold"]:
                    relay_on(config["relay_pin"])
                else:
                    relay_off(config["relay_pin"])
        time.sleep(config["interval"])

@app.route("/", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_hash = config["users"].get(username)
        if user_hash and check_password_hash(user_hash, password):
            session["username"] = username
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

def login_required(f):
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", devices=config["devices"], status=devices_status, interval=config["interval"], threshold=config["offline_threshold"])

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        interval = int(request.form.get("interval", config["interval"]))
        threshold = int(request.form.get("threshold", config["offline_threshold"]))
        config["interval"] = interval
        config["offline_threshold"] = threshold
        save_config(config)
        flash("Settings updated.")
        return redirect(url_for("settings"))
    return render_template("settings.html", interval=config["interval"], threshold=config["offline_threshold"], relay_pin=config["relay_pin"])

@app.route("/devices", methods=["POST"])
@login_required
def update_devices():
    ip = request.form.get("ip")
    name = request.form.get("name")
    relay = bool(request.form.get("relay"))
    if ip and name:
        config["devices"].append({"ip": ip, "name": name, "relay": relay, "offline_count": 0})
        devices_status[ip] = {"online": None, "last_ping": None, "response": None, "offline_count": 0}
        save_config(config)
    return redirect(url_for("dashboard"))

@app.route("/devices/remove/<ip>")
@login_required
def remove_device(ip):
    config["devices"] = [d for d in config["devices"] if d["ip"] != ip]
    devices_status.pop(ip, None)
    save_config(config)
    return redirect(url_for("dashboard"))

# Start background thread
threading.Thread(target=monitor_devices, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)