import os
import json
import threading
import time
import subprocess
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

import RPi.GPIO as GPIO

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('network_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"
DEVICES_FILE = "devices.json"

def load_config():
    """Load configuration from config.json file."""
    if not os.path.exists(CONFIG_FILE):
        logger.info("Config file not found, creating default configuration")
        default = {
            "interval": 30,
            "relay_pin": 17,
            "offline_threshold": 3,
            "users": {
                "admin": generate_password_hash("admin")
            }
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default, f, indent=2)
        logger.info("Default configuration created")
        return default
    
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        logger.info("Configuration loaded successfully")
        return config
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading config: {e}")
        return None

def save_config(cfg):
    """Save configuration to config.json file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
        logger.info("Configuration saved successfully")
    except IOError as e:
        logger.error(f"Error saving config: {e}")

def load_devices():
    """Load device list from devices.json file."""
    if not os.path.exists(DEVICES_FILE):
        logger.info("Devices file not found, creating default device list")
        default = [
            {"ip": "8.8.8.8", "name": "Google DNS", "relay": False, "offline_count": 0},
        ]
        with open(DEVICES_FILE, "w") as f:
            json.dump(default, f, indent=2)
        logger.info("Default device list created")
        return default
    
    try:
        with open(DEVICES_FILE) as f:
            devices = json.load(f)
        logger.info(f"Loaded {len(devices)} devices from file")
        return devices
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading devices: {e}")
        return []

def save_devices(devs):
    """Save device list to devices.json file."""
    try:
        with open(DEVICES_FILE, "w") as f:
            json.dump(devs, f, indent=2)
        logger.info(f"Saved {len(devs)} devices to file")
    except IOError as e:
        logger.error(f"Error saving devices: {e}")

config = load_config()
devices = load_devices()

# Ensure config loaded successfully
if not config:
    logger.critical("Failed to load configuration. Exiting.")
    exit(1)

devices_status = {d["ip"]: {"online": None, "last_ping": None, "response": None, "offline_count": 0} for d in devices}
status_lock = threading.Lock()
next_ping_time = time.time() + config["interval"]  # Track next ping time

app = Flask(__name__)
app.secret_key = os.urandom(24)

def ping(ip):
    """Ping an IP address and return success status and response time."""
    try:
        # Use shorter timeout and more restrictive ping parameters
        output = subprocess.check_output(
            ["ping", "-c", "1", "-W", "2", "-i", "0.2", ip], 
            stderr=subprocess.STDOUT, 
            universal_newlines=True,
            timeout=3  # Reduced timeout to 3 seconds
        )
        ms = None
        for line in output.splitlines():
            if "time=" in line:
                try:
                    ms = float(line.split("time=")[1].split()[0])
                    break
                except (IndexError, ValueError):
                    continue
        logger.info(f"Ping to {ip}: SUCCESS ({ms}ms)")
        return True, ms
    except subprocess.TimeoutExpired:
        logger.warning(f"Ping to {ip}: TIMEOUT (>3s)")
        return False, None
    except subprocess.CalledProcessError:
        logger.warning(f"Ping to {ip}: FAILED (host unreachable)")
        return False, None
    except Exception as e:
        logger.error(f"Ping to {ip}: ERROR ({e})")
        return False, None

def setup_gpio(pin):
    """Set up GPIO pin for relay control."""
    try:
        GPIO.setwarnings(False)  # Suppress GPIO warnings
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        relay_off(pin)
        logger.info(f"GPIO pin {pin} set up successfully for relay control")
        return True
    except Exception as e:
        logger.error(f"Error setting up GPIO pin {pin}: {e}")
        return False

def relay_on(pin):
    """Turn relay on."""
    try:
        GPIO.output(pin, GPIO.HIGH)
        logger.info(f"Relay turned ON (pin {pin})")
    except Exception as e:
        logger.error(f"Error turning relay on (pin {pin}): {e}")

def relay_off(pin):
    """Turn relay off."""
    try:
        GPIO.output(pin, GPIO.LOW)
        logger.info(f"Relay turned OFF (pin {pin})")
    except Exception as e:
        logger.error(f"Error turning relay off (pin {pin}): {e}")

def monitor_devices():
    """Main monitoring loop that pings devices and controls relay."""
    global next_ping_time
    
    if not setup_gpio(config["relay_pin"]):
        logger.warning("Failed to set up GPIO. Relay functionality will be disabled.")
        
    logger.info("Starting device monitoring loop")
    
    while True:
        try:
            # Set next ping time at the start of each cycle
            current_config = load_config()
            next_ping_time = time.time() + current_config["interval"]
            
            # Reload config and devices from files
            current_devices = load_devices()
            
            if not current_config or not current_devices:
                logger.error("Error loading configuration or devices. Skipping this cycle.")
                time.sleep(30)  # Wait before retrying
                continue
            
            with status_lock:
                # Ensure all devices have entries in devices_status
                for device in current_devices:
                    ip = device["ip"]
                    if ip not in devices_status:
                        devices_status[ip] = {"online": None, "last_ping": None, "response": None, "offline_count": 0}
                
                # Remove devices that no longer exist
                existing_ips = {d["ip"] for d in current_devices}
                for ip in list(devices_status.keys()):
                    if ip not in existing_ips:
                        del devices_status[ip]
            
            logger.info(f"Pinging {len(current_devices)} devices...")
            
            # Track ping cycle results for summary logging
            ping_results = {"success": 0, "failed": 0, "total": len(current_devices)}
            
            for device in current_devices:
                ip = device["ip"]
                online, response = ping(ip)
                
                # Update ping results counter
                if online:
                    ping_results["success"] += 1
                else:
                    ping_results["failed"] += 1
                
                with status_lock:
                    status = devices_status[ip]
                    prev_online = status["online"]
                    status["response"] = response
                    
                    if not online:
                        status["offline_count"] += 1
                        # Only change status to offline after reaching threshold
                        if status["offline_count"] >= current_config["offline_threshold"]:
                            if prev_online is not False:  # Just went offline
                                logger.warning(f"Device {device['name']} ({ip}) went OFFLINE after {status['offline_count']} failed pings")
                            status["online"] = False
                        # If under threshold, keep previous online status or set to None if first time
                        elif prev_online is None:
                            status["online"] = None
                        else:
                            logger.info(f"Device {device['name']} ({ip}) ping failed ({status['offline_count']}/{current_config['offline_threshold']})")
                    else:
                        # Ping successful - device is online
                        if prev_online is False:  # Just came online
                            logger.info(f"Device {device['name']} ({ip}) came ONLINE")
                        elif status["offline_count"] > 0:
                            logger.info(f"Device {device['name']} ({ip}) ping recovered after {status['offline_count']} failures")
                        status["online"] = True
                        status["offline_count"] = 0
                        # Only update last_ping timestamp on successful ping
                        status["last_ping"] = time.strftime("%Y-%m-%d %H:%M:%S")

                    # Relay logic
                    if device.get("relay", False):
                        if status["offline_count"] >= current_config["offline_threshold"]:
                            logger.warning(f"Device {device['name']} offline for {status['offline_count']} cycles, triggering relay")
                            relay_on(current_config["relay_pin"])
                        else:
                            relay_off(current_config["relay_pin"])
            
            # Log ping cycle summary
            logger.info(f"Ping cycle complete: {ping_results['success']}/{ping_results['total']} devices online, {ping_results['failed']} failed. Next ping in {current_config['interval']} seconds")
            time.sleep(current_config["interval"])
        
        except Exception as e:
            logger.error(f"Error in monitor_devices: {e}")
            next_ping_time = time.time() + 30  # Set next ping time for retry
            time.sleep(30)  # Wait before retrying

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
            logger.info(f"User {username} logged in successfully from {request.remote_addr}")
            return redirect(url_for("dashboard"))
        logger.warning(f"Failed login attempt for user {username} from {request.remote_addr}")
        flash("Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    username = session.get("username", "unknown")
    session.pop("username", None)
    logger.info(f"User {username} logged out")
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
    devices = load_devices()
    with status_lock:
        status_copy = devices_status.copy()
    return render_template("dashboard.html", devices=devices, status=status_copy, interval=config["interval"], threshold=config["offline_threshold"])

@app.route("/api/status")
@login_required
def api_status():
    try:
        devices = load_devices()
        with status_lock:
            status_copy = devices_status.copy()
        
        # Calculate countdown to next ping
        time_until_next_ping = max(0, int(next_ping_time - time.time()))
        
        return {
            "devices": devices, 
            "status": status_copy, 
            "interval": config["interval"], 
            "threshold": config["offline_threshold"],
            "countdown": time_until_next_ping
        }
    except Exception as e:
        logger.error(f"Error in api_status: {e}")
        return {
            "devices": [], 
            "status": {}, 
            "interval": config.get("interval", 30), 
            "threshold": config.get("offline_threshold", 3),
            "countdown": 0
        }, 500

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Handle settings page and configuration updates."""
    if request.method == "POST":
        # Check if password change was requested
        if request.form.get("change_password"):
            new_password = request.form.get("new_password", "").strip()
            if new_password and len(new_password) >= 4:
                config["users"]["admin"] = generate_password_hash(new_password, method="pbkdf2:sha256")
                save_config(config)
                logger.info(f"Admin password changed by user {session.get('username')}")
                flash("Admin password updated successfully.")
            else:
                flash("Password must be at least 4 characters long.")
            return redirect(url_for("settings"))
        
        # Otherwise, update general settings
        try:
            interval = int(request.form.get("interval", config["interval"]))
            threshold = int(request.form.get("threshold", config["offline_threshold"]))
            
            # Validate input ranges
            if interval < 5:
                flash("Interval must be at least 5 seconds.")
                return redirect(url_for("settings"))
            if threshold < 1:
                flash("Offline threshold must be at least 1.")
                return redirect(url_for("settings"))
            
            old_interval = config["interval"]
            old_threshold = config["offline_threshold"]
            
            config["interval"] = interval
            config["offline_threshold"] = threshold
            save_config(config)
            
            logger.info(f"Settings updated by user {session.get('username')}: interval {old_interval}→{interval}, threshold {old_threshold}→{threshold}")
            flash("Settings updated successfully.")
            
        except ValueError:
            flash("Invalid input values. Please enter valid numbers.")
        
        return redirect(url_for("settings"))
    
    return render_template("settings.html", 
                         interval=config["interval"], 
                         threshold=config["offline_threshold"], 
                         relay_pin=config["relay_pin"])

@app.route("/devices", methods=["POST"])
@login_required
def update_devices():
    """Add a new device to the monitoring list."""
    ip = request.form.get("ip", "").strip()
    name = request.form.get("name", "").strip()
    relay = bool(request.form.get("relay"))
    
    if not ip or not name:
        flash("Both IP address and name are required.")
        return redirect(url_for("dashboard"))
    
    # Basic IP validation
    import re
    ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if not re.match(ip_pattern, ip) and not ip.replace('.', '').replace('-', '').replace('_', '').isalnum():
        flash("Invalid IP address format.")
        return redirect(url_for("dashboard"))
    
    devices = load_devices()
    
    # Check if device already exists
    if any(d["ip"] == ip for d in devices):
        flash(f"Device with IP {ip} already exists.")
        return redirect(url_for("dashboard"))
    
    devices.append({"ip": ip, "name": name, "relay": relay, "offline_count": 0})
    
    with status_lock:
        devices_status[ip] = {"online": None, "last_ping": None, "response": None, "offline_count": 0}
    
    save_devices(devices)
    logger.info(f"User {session.get('username')} added device: {name} ({ip}), relay: {relay}")
    flash(f"Device '{name}' added successfully.")
    return redirect(url_for("dashboard"))

@app.route("/devices/edit/<ip>", methods=["GET", "POST"])
@login_required
def edit_device(ip):
    devices = load_devices()
    device = next((d for d in devices if d["ip"] == ip), None)
    if not device:
        flash("Device not found.")
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        # Update device parameters
        old_name = device["name"]
        old_relay = device["relay"]
        
        new_name = request.form.get("name", "").strip()
        if not new_name:
            flash("Device name cannot be empty.")
            return render_template("edit_device.html", device=device)
        
        device["name"] = new_name
        device["relay"] = bool(request.form.get("relay"))
        save_devices(devices)
        
        logger.info(f"User {session.get('username')} updated device {ip}: name '{old_name}'→'{new_name}', relay {old_relay}→{device['relay']}")
        flash(f"Device '{device['name']}' updated successfully.")
        return redirect(url_for("dashboard"))
    
    # For GET request, render edit form
    return render_template("edit_device.html", device=device)

@app.route("/devices/remove/<ip>")
@login_required
def remove_device(ip):
    devices = load_devices()
    device_name = next((d["name"] for d in devices if d["ip"] == ip), ip)
    devices = [d for d in devices if d["ip"] != ip]
    
    with status_lock:
        devices_status.pop(ip, None)
    
    save_devices(devices)
    logger.info(f"User {session.get('username')} removed device: {device_name} ({ip})")
    return redirect(url_for("dashboard"))

# Start background monitoring thread
monitoring_thread = threading.Thread(target=monitor_devices, daemon=True)
monitoring_thread.start()

if __name__ == "__main__":
    logger.info("Starting Network Monitor...")
    logger.info(f"Dashboard will be available at: http://localhost:5000")
    logger.info(f"Monitoring {len(devices)} devices every {config['interval']} seconds")
    logger.info("Press Ctrl+C to stop")
    
    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        logger.info("Shutting down Network Monitor...")
        try:
            GPIO.cleanup()
            logger.info("GPIO cleanup completed")
        except:
            pass