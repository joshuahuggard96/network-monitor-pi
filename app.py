import socket


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
    print("Authentication failed. Please try again.")

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)


print("\nSystem Information:")
print(f"Hostname: {hostname}")
print(f"IP Address: {ip_address}")