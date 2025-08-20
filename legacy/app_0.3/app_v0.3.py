import threading
import time
import json
from ping3 import ping
from flask import Flask, render_template, jsonify

app = Flask(__name__)

## Variables
ping_interval = 1  # seconds
times_to_check = 2
ip_address_list = ["192.168.16.1", "8.8.8.8", "192.168.16.42","192.168.51.122"]
toggle_ping_list = True  # Set to True to enable automated pinging
result = False
ip_status = {}

## Function to ping an IP address
def ping_ip(ipaddress):
  response = ping(ipaddress)
  if response is not None and response is not False:
      print(f"Ping to {ipaddress} successful. ✅")
      ip_status[ipaddress] = True
      return True
  else:
      print(f"Ping to {ipaddress} failed. ❌")
      ip_status[ipaddress] = False
      return False

def ping_ip_list(ip_list):
    list_result = True
    for ip in ip_list:
        if ping_ip(ip) == False:
            list_result = False
    return list_result

def automate_ping_list(ip_list):
    print("pinging IP List:")
    list_result = ping_ip_list(ip_list)
    time.sleep(ping_interval)
    return list_result

def ping_list_check(ip_list):
    times_passed = 0
    global result
    while toggle_ping_list:
        ping_list_passed = automate_ping_list(ip_list)
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
    ping_thread = threading.Thread(target=ping_list_check, args=(ip_address_list,), daemon=True)
    ping_thread.start()
    
    print("Network Monitoring started")
    print("web server accessable on Localhost:5000")

    app.run(host='0.0.0.0', port=5000, debug=False)


