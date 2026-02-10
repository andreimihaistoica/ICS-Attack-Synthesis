import subprocess

def find_plc_ip():
    # Perform a network scan to find the PLC
    network_scan = subprocess.run(['nmap', '-sn', '192.168.1.0/24'], capture_output=True, text=True)
    output = network_scan.stdout

    # Parse the output to find the PLC's IP address
    for line in output.splitlines():
        if "Nmap scan report for" in line:
            ip_address = line.split()[-1]
            print(f"Found PLC at IP: {ip_address}")
            return ip_address

    print("PLC not found on the network.")
    return None

plc_ip = find_plc_ip()
if not plc_ip:
    exit(1)