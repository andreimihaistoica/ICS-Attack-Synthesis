import socket
import struct
import subprocess

def find_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1.0/24"
    
    # Use nmap to scan the subnet for devices
    nmap_output = subprocess.check_output(["nmap", "-sn", subnet])
    
    # Parse the output to find the PLC's IP address
    for line in nmap_output.splitlines():
        if b"Siemens S7-1200" in line:
            ip_address = line.split()[0].decode('utf-8')
            return ip_address

    return None

plc_ip = find_plc_ip()
if plc_ip:
    print(f"PLC IP Address: {plc_ip}")
else:
    print("PLC not found on the network.")