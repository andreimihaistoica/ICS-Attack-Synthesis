import os
import socket
import subprocess
from ipaddress import ip_network

def find_plc_ip(network_range):
    """Scan the network to find the Siemens S7-1200 PLC."""
    for ip in ip_network(network_range).hosts():
        ip = str(ip)
        try:
            # Attempt to connect to the PLC on port 102 (S7 protocol)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((ip, 102))
                print(f"Found Siemens S7-1200 PLC at IP: {ip}")
                return ip
        except (socket.timeout, ConnectionRefusedError):
            continue
    print("No Siemens S7-1200 PLC found on the network.")
    return None

def ping_sweep(ip):
    """Perform a ping sweep on the specified IP address."""
    try:
        # Ping the IP address once
        subprocess.check_call(['ping', '-c', '1', ip], stdout=subprocess.DEVNULL)
        print(f"Ping to {ip} successful.")
    except subprocess.CalledProcessError:
        print(f"Ping to {ip} failed.")

def main():
    # Define the network range to scan (e.g., '192.168.1.0/24')
    network_range = '192.168.1.0/24'
    
    # Find the PLC's IP address
    plc_ip = find_plc_ip(network_range)
    
    if plc_ip:
        # Perform a ping sweep on the PLC's IP address
        ping_sweep(plc_ip)

if __name__ == "__main__":
    main()