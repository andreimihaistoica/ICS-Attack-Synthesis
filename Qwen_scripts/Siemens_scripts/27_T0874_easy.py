import socket
import subprocess

def find_plc_ip():
    # Assuming the PLC is on the same network and responds to pings
    network = "192.168.1.0/24"  # Change this to your network range
    command = f"arp -a {network}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    for line in result.stdout.splitlines():
        if "PLC" in line:  # Replace "PLC" with a keyword that identifies your PLC
            ip_address = line.split()[0]
            return ip_address
    
    return None

plc_ip = find_plc_ip()
if plc_ip:
    print(f"PLC IP Address: {plc_ip}")
else:
    print("PLC not found on the network.")