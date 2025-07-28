import socket
import subprocess

## Variables
admin_user = "admin"
admin_password = "admin"
logged_in = False
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
ip_address_list = []


## Function to authenticate user
def authenticate(username, password):
    if username == admin_user and password == admin_password:
        return True
    return False

## Function to ping an IP address note: -n is used for Windows, use -c for Linux/Mac
def Ping_IP(IPaddress):
    try:
        output = subprocess.check_output(["ping", "-n", "2", IPaddress])
        print(f"{output.decode()}\nPing successful: ✅")
    except subprocess.CalledProcessError:
        print("Ping failed: ❌")


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
    print("Login successful ✅")
    logged_in = True
  else:
    print("Authentication failed. Please try again. ❌")



print("\nSystem Information:")
print(f"Hostname: {hostname}")
print(f"IP Address: {ip_address}")

while True:
    print("\nMenu:")
    print("1. List IP addresses")
    print("2. Ping an IP address")
    print("3. Ping IP address List")
    print("4. add IP address to list")
    print("5. Exit")
    
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
        print("Pinging IP address list...")
        if not ip_address_list:
            print("No IP addresses to ping. ❌")
        else:
          for ip in ip_address_list:
            Ping_IP(ip)
    elif choice == "4":
        new_ip = input("Enter the IP address to add: ")
        ip_address_list.append(new_ip)
        print(f"IP Address {new_ip} added to the list. ✅")
    elif choice == "5":
        print("Exiting the Admin Panel. Goodbye! 👋")
        break
    else:
        print("Invalid choice. Please try again. ❌")