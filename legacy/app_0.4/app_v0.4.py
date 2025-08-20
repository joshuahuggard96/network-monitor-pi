import threading
import time
from ping3 import ping
from flask import Flask, render_template, jsonify
import socket 
import logging

app = Flask(__name__)

## Variables
ping_interval = 1  # seconds
times_to_check = 2
toggle_ping_list = True  # Set to True to enable automated pinging
result = False
ip_status = {}

ip_address_list = {
    "Router": "10.220.14.1",
    "Google DNS": "8.8.8.8", 
    "Desktop PC": "10.220.14.28"
}


## Function to ping an IP address
def ping_ip(ipaddress):
  response = ping(ipaddress)
  if response is not None and response is not False:
      ip_status[ipaddress] = True
      return True
  else:
      ip_status[ipaddress] = False
      return False

def ping_ip_list(ip_list):
    list_result = True
    for name, ip in ip_list.items():
        if ping_ip(ip) == False:
            list_result = False
    return list_result

def ping_list_check(ip_list):
    times_passed = 0
    global result
    while toggle_ping_list:
        ping_list_passed = ping_ip_list(ip_list)
        time.sleep(ping_interval)
        if ping_list_passed:
            times_passed += 1
            if times_passed >= times_to_check:
                result = True
        else:
            times_passed = 0
            result = False
    return result



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify({
        'network_status': result,
        'timestamp': time.time(),
        'ip_addresses': ip_address_list,
        'ip_status': ip_status
    })


if __name__ == '__main__':

    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    ping_thread = threading.Thread(target=ping_list_check, args=(ip_address_list,), daemon=True)
    ping_thread.start()
    
    print("Network Monitoring started")
    print("web server accessable on Localhost:5000")

    app.run(host='0.0.0.0', port=5000, debug=False)


