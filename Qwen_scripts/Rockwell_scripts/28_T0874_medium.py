import subprocess

def find_plc_ip():
    # Define the network range to scan
    network_range = "192.168.1.0/24"  # Adjust this to your network range

    # Use nmap to scan the network
    nmap_command = f"nmap -p 502 {network_range} --open"
    result = subprocess.run(nmap_command, shell=True, capture_output=True, text=True)

    # Parse the output to find the IP address of the PLC
    for line in result.stdout.splitlines():
        if "502/tcp open" in line:
            ip_address = line.split()[0]
            return ip_address

    return None

plc_ip = find_plc_ip()
if plc_ip:
    print(f"PLC IP Address: {plc_ip}")
else:
    print("PLC not found on the network.")