import socket
import struct
from pycomm3 import LogixDriver, S7

def find_plc_ip():
    # Define the network range to scan
    network_range = "192.168.1.0/24"
    
    # Convert the network range to a list of IP addresses
    ip_list = [f"192.168.1.{i}" for i in range(1, 255)]
    
    # Function to check if an IP address is a PLC
    def is_plc(ip):
        try:
            with S7(ip) as plc:
                if plc.is_connected:
                    return True
        except:
            return False
    
    # Scan the network
    for ip in ip_list:
        if is_plc(ip):
            return ip
    
    return None

# Find the PLC's IP address
plc_ip = find_plc_ip()
if plc_ip:
    print(f"PLC found at IP address: {plc_ip}")
else:
    print("PLC not found on the network.")