import socket
import pycomm3
from pycomm3 import LogixDriver, SLC500Driver, PLC
from pycomm3.cip.cip import CIPError

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    
    # Scan the subnet for devices
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the IP address
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((ip, 102))  # Port 102 is the default for S7-1200
                if result == 0:
                    print(f"PLC found at IP: {ip}")
                    return ip
        except socket.error:
            continue
    return None

# Function to change the PLC's password
def change_plc_password(ip, new_password):
    try:
        # Connect to the PLC
        with PLC(ip) as plc:
            # Change the password
            plc.set_plc_password(new_password)
            print(f"Password changed successfully to: {new_password}")
    except CIPError as e:
        print(f"Error changing password: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Define the new password
        new_password = "NewSecurePassword123"
        
        # Change the PLC's password
        change_plc_password(plc_ip, new_password)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()