import socket
import time
from pycomm3 import LogixDriver

def find_plc_ip():
    # Define the possible IP range for the PLC
    ip_range = "192.168.1."
    for i in range(1, 255):
        ip_address = ip_range + str(i)
        try:
            # Attempt to connect to the PLC on port 44818 (Allen-Bradley)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((ip_address, 44818))
                print(f"Found PLC at IP: {ip_address}")
                return ip_address
        except:
            continue
    print("PLC not found in the specified IP range.")
    return None

def collect_tags(plc_ip):
    # Connect to the PLC using the found IP address
    with LogixDriver(plc_ip) as plc:
        # Read all tags from the PLC
        tags = plc.get_tag_list()
        for tag in tags:
            tag_name = tag['tag_name']
            tag_value = plc.read(tag_name)
            print(f"Tag: {tag_name}, Value: {tag_value}")

def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        # Step 2: Collect and print tag values
        collect_tags(plc_ip)

if __name__ == "__main__":
    main()