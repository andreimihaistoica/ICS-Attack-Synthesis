import subprocess
import re

def find_plc_ip():
    # Use arp-scan or nmap to find devices on the network
    command = "arp-scan --localnet"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Example output parsing (adjust based on your network)
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    ips = ip_pattern.findall(result.stdout)
    
    # Assume the PLC has a specific MAC address prefix (e.g., Rockwell)
    for ip in ips:
        mac_command = f"arp -a {ip}"
        mac_result = subprocess.run(mac_command, shell=True, capture_output=True, text=True)
        if "00-1D-9C" in mac_result.stdout:  # Example Rockwell MAC prefix
            return ip
    
    return None

plc_ip = find_plc_ip()
if plc_ip:
    print(f"Found PLC IP: {plc_ip}")
else:
    print("PLC not found on the network.")