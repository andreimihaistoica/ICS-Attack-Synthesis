import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (adjust as needed)
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the IP address
            with socket.create_connection((ip, 44818), timeout=1) as sock:
                print(f"PLC found at IP: {ip}")
                return ip
        except (socket.timeout, ConnectionRefusedError, OSError):
            continue
    print("PLC not found in the specified subnet.")
    return None

# Function to read tag values from the PLC
def read_tag_values(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            # List of tags to read (adjust as needed)
            tags = ['Tag1', 'Tag2', 'Tag3']
            tag_values = plc.read(*tags)
            for tag, value in tag_values:
                print(f"Tag: {tag}, Value: {value}")
    except Exception as e:
        print(f"Error reading tag values: {e}")

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        read_tag_values(plc_ip)

if __name__ == "__main__":
    main()