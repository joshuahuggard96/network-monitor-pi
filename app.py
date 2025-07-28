import socket
import subprocess

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



admin_user = "admin"
admin_password = "admin"
logged_in = False



def authenticate(username, password):
    if username == admin_user and password == admin_password:
        return True
    return False

while not logged_in:
  if authenticate(input("Enter username: "), input("Enter password: ")):
    print("Login successful")
    logged_in = True
  else:
    print("Authentication failed. Please try again. ❌")

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)


print("\nSystem Information:")
print(f"Hostname: {hostname}")
print(f"IP Address: {ip_address}")

## Function to ping an IP address note: -n is used for Windows, use -c for Linux/Mac
def Ping_IP(IPaddress):
    try:
        output = subprocess.check_output(["ping", "-n", "2", IPaddress])
        print(f"{output.decode()}\nPing successful: ✅")
    except subprocess.CalledProcessError:
        print("Ping failed.❌")

while True:
    print("\nMenu:")
    print("1. Ping an IP address")
    print("2. Exit")
    
    choice = input("Enter your choice: ")
    
    if choice == "1":
        ip_to_ping = input("Enter the IP address to ping: ")
        Ping_IP(ip_to_ping)
    elif choice == "2":
        print("Exiting the Admin Panel. Goodbye! 👋")
        break
    else:
        print("Invalid choice. Please try again. ❌")