import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the IP address of the PLC
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    
    # Scan the subnet for devices
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((ip, 44818))  # 44818 is the default port for EtherNet/IP
                if result == 0:
                    print(f"PLC found at IP: {ip}")
                    return ip
        except socket.error:
            continue
    print("PLC not found on the network.")
    return None

# Function to change the PLC credentials
def change_plc_credentials(ip, new_password):
    try:
        # Connect to the PLC
        with LogixDriver(ip) as plc:
            # Change the password (this is a simplified example)
            # Note: The actual method to change the password may vary depending on the PLC model and firmware
            plc.write("Password", new_password)
            print(f"Password changed to: {new_password}")
    except Exception as e:
        print(f"Failed to change password: {e}")

# Main function
def main():
    # Discover the PLC IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Define the new password
        new_password = "NewSecurePassword123"
        
        # Change the PLC credentials
        change_plc_credentials(plc_ip, new_password)

if __name__ == "__main__":
    main()