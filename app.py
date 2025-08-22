import threading
import time
from ping3 import ping
from flask import Flask, render_template, jsonify
import logging
from devices import device_list

app = Flask(__name__)

## Variables
ping_interval = 0.5  # seconds
output_status = False  # Initialize the output status


## Function to ping an IP address
def ping_device(device):
  ip = device["ip"]
  response = ping(ip)
  timestamp = time.strftime("%d %b %Y %H:%M:%S")
  if response:
    device["status"] = True
    device["last_online"] = timestamp
  else:
    device["status"] = False



## Fuction to ping list 
def ping_device_list(list):
    global output_status
    while True:
       all_devices_online = True
       for device in list.values():
          ping_device(device)
          if device["status"] == False:
             all_devices_online = False
          print(device["status"])
       output_status = all_devices_online
       print(f"relay on {output_status}")
       time.sleep(ping_interval)






@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify({
        'output_status': output_status,
        'timestamp': time.time(),
        'device_list': device_list
    })

@app.route('/api/status-html')
def get_status_html():
    """Return HTML fragment instead of JSON"""
    try:
        # Get the current status data
        status_data = {
            'output_status': output_status,
            'timestamp': time.time(),
            'device_list': device_list
        }
        
        # Build the HTML response
        html_parts = []
        
        # Status section
        if status_data['output_status']:
            html_parts.append('<div class="status online">Relay Status ON</div>')
        else:
            html_parts.append('<div class="status offline">Relay Status OFF</div>')
        
        # Device list section
        html_parts.append('<div id="ip-list"><h3>Device Status:</h3>')
        
        for device_name, device_info in status_data['device_list'].items():
            if device_info['status'] is True:
                css_class = 'ip-item ip-online'
                status_text = 'Online'
            elif device_info['status'] is False:
                css_class = 'ip-item ip-offline'
                status_text = 'Offline'
            else:
                css_class = 'ip-item ip-checking'
                status_text = 'Checking'
            
            device_html = f'''
            <div class="{css_class}">
                <strong>{device_name}</strong> 
                <span class="status-indicator">{status_text}</span>
            </div>
            '''
            html_parts.append(device_html)
        
        html_parts.append('</div>')  # Close ip-list
        
        return ''.join(html_parts)
        
    except Exception as e:
        return f'<div class="status offline">Error checking status: {str(e)}</div>'

if __name__ == '__main__':

    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    ping_thread = threading.Thread(target=ping_device_list, args=(device_list,), daemon=True)
    ping_thread.start()
    
    print("Network Monitoring started")
    print("web server accessable on Localhost:5000")

    app.run(host='0.0.0.0', port=5000, debug=False)


