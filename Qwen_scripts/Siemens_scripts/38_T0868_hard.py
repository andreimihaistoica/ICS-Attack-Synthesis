import socket
import pycomm3
from pycomm3 import LogixDriver, SLC500Driver, PLC

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    
    # Scan the subnet for devices
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with PLC(ip) as plc:
                if plc.open():
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            continue
    return None

# Function to read the operating mode of the PLC
def read_operating_mode(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            # Read the operating mode
            operating_mode = plc.read_tag('ST')
            if operating_mode:
                print(f"Operating Mode: {operating_mode.value}")
            else:
                print("Failed to read operating mode.")
    except Exception as e:
        print(f"Error reading operating mode: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Read the operating mode
        read_operating_mode(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()