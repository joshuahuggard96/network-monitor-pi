import socket
import subprocess
import time

## Variables
admin_user = "admin"
admin_password = "admin"
logged_in = False
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
ip_address_list = [ip_address, "192.168.0.2","192.168.0.1"]
ping_interval = 10  # seconds
automate_ping_list = True  # Set to True to enable automated pinging


## Function to authenticate user
def authenticate(username, password):
    if username == admin_user and password == admin_password:
        return True
    return False


## Function to ping an IP address note: 
def Ping_IP(IPaddress):
    try:
        output = subprocess.check_output(["ping", "-c", "1", IPaddress], stderr=subprocess.STDOUT, text=True)
        if "1 received" in output:
            print(f"Ping to {IPaddress} successful. ✅")
            return True
        else:
            print(f"Ping to {IPaddress} failed. ❌")
            return False
    except subprocess.CalledProcessError as e:
        # This catches when ping command fails (unreachable hosts, timeouts, etc.)
        output = e.output if e.output else ""
        if "unreachable" in output.lower():
            print(f"Ping to {IPaddress} - Host unreachable. ❌")
        elif "100% packet loss" in output or "0 received" in output:
            print(f"Ping to {IPaddress} - Request timed out. ❌")
        elif "name or service not known" in output.lower():
            print(f"Ping to {IPaddress} - Unknown host. ❌")
        else:
            print(f"Ping to {IPaddress} failed. ❌")
        return False
    except Exception as e:
        print(f"Ping to {IPaddress} - Error: {e}")
        return False
    
## Function to ping a list of IP addresses
def Ping_IP_List(ip_list):
    list_result = True
    for ip in ip_list:
        if not Ping_IP(ip):
            list_result = False
    if not list_result:
        print(f"Ping List Failed. ❌")
    else:
        print(f"Ping List Success. ✅")
    return list_result

## Function to automate pinging the list of IP addresses DOESNT WORK YET
def automate_ping_list(ip_list):
    wait_time = ping_interval
    Ping_IP_List(ip_list)
    if logged_in:
        print(f"Waiting for {wait_time} seconds before the next ping...")
        time.sleep(wait_time)


## Print the welcome message
print(r"""
    
  _   _      _                      _                
 | \ | | ___| |___      _____  _ __| | __            
 |  \| |/ _ \ __\ \ /\ / / _ \| '__| |/ /            
 | |\  |  __/ |_ \ V  V / (_) | |  |   <             
 |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\    ____  _ 
 |  \/  | __ _ _ __   __ _  __ _  ___ _ __  |  _ \(_)
 | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__| | |_) | |
 | |  | | (_| | | | | (_| | (_| |  __/ |    |  __/| |
 |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|    |_|   |_|
                           |___/                     

""")


print("Welcome to the Admin Panel")

## Prompt for authentication
while not logged_in:
  if authenticate(input("Enter username: "), input("Enter password: ")):
    print("Login successful.")
    logged_in = True
  else:
    print("Authentication failed. Please try again.")



print("\nSystem Information:")
print(f"Hostname: {hostname}")
print(f"IP Address: {ip_address}")

while True:
    print("\nMenu:")
    print("1. List IP addresses")
    print("2. Ping an IP address")
    print("3. Ping IP address List")
    print("4. add IP address to list")
    print("5. enable/disable automated pinging")
    print("6. Exit")

    choice = input("Enter your choice: ")
    
    if choice == "1":
        print("Listing IP addresses...")
        if not ip_address_list:
            print("No IP addresses found. ❌")
        else:
            for ip in ip_address_list:
                print(f"IP Address: {ip}")

    elif choice == "2":
        ip_to_ping = input("Enter the IP address to ping: ")
        Ping_IP(ip_to_ping)

    elif choice == "3":
        print("Pinging IP address list: ")
        if not ip_address_list:
            print("No IP addresses to ping. ❌")
        else:
            Ping_IP_List(ip_address_list)

    elif choice == "4":
        new_ip = input("Enter the IP address to add: ")
        ip_address_list.append(new_ip)
        print(f"IP Address {new_ip} added to the list. ✅")

    elif choice == "5":
        automate_ping_list = not automate_ping_list
        if automate_ping_list:
            print("Automated pinging enabled. ✅")
        else:
            print("Automated pinging disabled. ❌")
            
    elif choice == "6" or choice.lower() == "exit":
        print("Exiting the Admin Panel. Goodbye! 👋")
        break
    else:
        print("Invalid choice. Please try again. ❌")