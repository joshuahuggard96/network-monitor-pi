import threading
import logging
import time
import socket
import subprocess
from ping3 import ping ,verbose_ping

## Variables
ping_interval = 1  # seconds
times_to_check = 2 # number of times to check before confirming the IPs are reachable
automate_ping_list = True  # Set to True to enable automated pinging
ip_address_list = ["192.168.0.1", "192.168.0.2", "192.168.0.3"]
toggle_ping_list = True  # Set to True to enable automated pinging
result = False
debug = False  # Set to True to enable debug mode

logging.basicConfig(filename='monitor.log', level=logging.INFO, format='%(asctime)s - %(message)s')

## Function to ping an IP address
def ping_ip(ipaddress):
  response = ping(ipaddress)
  if response is not None and response is not False:
      if debug: 
          logging.info(f"Ping to {ipaddress} successful. ✅")
      return True
  else:
      if debug:
          logging.info(f"Ping to {ipaddress} failed. ❌")
      return False

def ping_ip_list(ip_list):
    list_result = True
    for ip in ip_list:
        if ping_ip(ip) == False:
            list_result = False
    return list_result

def automate_ping_list(ip_list):
    list_result = ping_ip_list(ip_list)
    time.sleep(ping_interval)
    return list_result

def ping_list_check(ip_list):
    global result, times_passed
    times_passed = 0
    while toggle_ping_list:
        if debug:
            logging.info(f"times passed: {times_passed} and ping list out: {result}")
        ping_list_passed = automate_ping_list(ip_list)
        if ping_list_passed and times_passed < times_to_check:
            times_passed += 1
            result = False
        elif ping_list_passed and times_passed >= times_to_check:
            times_passed += 1
            result = True
        else:
            times_passed = 0
            result = False
    return result

ping_thread = threading.Thread(target=ping_list_check, args=(ip_address_list,), daemon=True)
ping_thread.start()

print("ping monitoring started in background")
while True:
    user_input = input("enter 'stop' to quit or press Enter to continue: ")
    if user_input.lower() == "stop":
        toggle_ping_list = False
        break
    elif user_input.lower() == "debug":
        debug = not debug  # This toggles True/False properly
        print(f"Debug mode: {'ON' if debug else 'OFF'}")
    else:
        print(f"Current result: {result}")

