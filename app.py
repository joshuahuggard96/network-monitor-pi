"""
Network Monitor Application

A Flask-based web application that monitors network devices by pinging them
and provides a web interface for device management.

Author: Joshua Huggard
Date: August 2025
"""

import threading
import time
import logging
from ping3 import ping
from flask import Flask, render_template, jsonify, request

from devices import device_list

# Configuration
PING_INTERVAL = 0.5
HOST = '0.0.0.0'
PORT = 5000

# Flask app initialization
app = Flask(__name__)

# Global variables
output_status = False
device_lock = threading.Lock()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_devices_to_file():
    """Save the current device list to devices.py file."""
    try:
        with open('devices.py', 'w') as file:
            file.write('# Network Monitor Device Configuration\n')
            file.write('# Auto-generated file - modify with caution\n\n')
            file.write('device_list = {\n')
            
            for device_name, device_info in device_list.items():
                file.write(f'    "{device_name}": {{\n')
                file.write(f'        "ip": "{device_info["ip"]}",\n')
                file.write(f'        "status": None,\n')
                file.write(f'        "last_online": None\n')
                file.write(f'    }},\n')
            
            file.write('}\n')
        
        logger.info("Device list successfully saved to devices.py")
        
    except Exception as error:
        logger.error(f"Failed to save devices.py: {error}")


def ping_device(device):
    """Ping a single device and update its status."""
    ip_address = device["ip"]
    response = ping(ip_address)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    if response:
        device["status"] = True
        device["last_online"] = timestamp
        logger.debug(f"Device {ip_address} is online")
    else:
        device["status"] = False
        logger.debug(f"Device {ip_address} is offline")


def ping_device_list():
    """Continuously ping all devices and update global status."""
    global output_status
    
    logger.info("Starting device monitoring thread")
    
    while True:
        all_devices_online = True
        
        
        with device_lock:
            devices_copy = dict(device_list)
        
        for device_name, device in devices_copy.items():
            ping_device(device)
            if not device["status"]:
                all_devices_online = False
        
        output_status = all_devices_online
        logger.debug(f"Overall network status: {'Online' if output_status else 'Offline'}")
        
        time.sleep(PING_INTERVAL)


@app.route('/')
def index():
    """Serve the main dashboard page."""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """API endpoint to get current network status."""
    with device_lock:
        device_list_copy = dict(device_list)
    
    return jsonify({
        'output_status': output_status,
        'timestamp': time.time(),
        'device_list': device_list_copy
    })


@app.route('/api/add-device', methods=['POST'])
def add_device():
    """API endpoint to add a new device to the monitoring list."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        device_name = data.get('name')
        device_ip = data.get('ip')
        
        if not device_name or not device_ip:
            return jsonify({'success': False, 'error': 'Both name and IP are required'}), 400
        
        # Validate IP format
        ip_parts = device_ip.split('.')
        if len(ip_parts) != 4 or not all(part.isdigit() and 0 <= int(part) <= 255 for part in ip_parts):
            return jsonify({'success': False, 'error': 'Invalid IP address format'}), 400
        
        with device_lock:
            if device_name in device_list:
                return jsonify({'success': False, 'error': 'Device name already exists'}), 400
            
            for existing_device in device_list.values():
                if existing_device['ip'] == device_ip:
                    return jsonify({'success': False, 'error': 'IP address already exists'}), 400
            
            device_list[device_name] = {
                "ip": device_ip,
                "status": None,
                "last_online": None
            }
            
            save_devices_to_file()
        
        logger.info(f"Added new device: {device_name} ({device_ip})")
        
        return jsonify({
            'success': True, 
            'message': f'Device "{device_name}" added successfully'
        })
        
    except Exception as error:
        logger.error(f"Error adding device: {error}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/remove-device', methods=['POST'])
def remove_device():
    """API endpoint to remove a device from the monitoring list."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        device_name = data.get('name')
        
        if not device_name:
            return jsonify({'success': False, 'error': 'Device name is required'}), 400
        
        with device_lock:
            if device_name not in device_list:
                return jsonify({'success': False, 'error': 'Device not found'}), 404
            
            removed_device = device_list.pop(device_name)
            save_devices_to_file()
        
        logger.info(f"Removed device: {device_name} ({removed_device['ip']})")
        
        return jsonify({
            'success': True, 
            'message': f'Device "{device_name}" removed successfully'
        })
        
    except Exception as error:
        logger.error(f"Error removing device: {error}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


def main():
    """Main application entry point."""
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.setLevel(logging.ERROR)
    
    ping_thread = threading.Thread(
        target=ping_device_list, 
        daemon=True, 
        name="PingMonitorThread"
    )
    ping_thread.start()
    
    logger.info("Network Monitor started")
    logger.info(f"Web interface available at http://localhost:{PORT}")
    logger.info(f"Monitoring {len(device_list)} devices")
    
    app.run(host=HOST, port=PORT, debug=False, threaded=True)


if __name__ == '__main__':
    main()