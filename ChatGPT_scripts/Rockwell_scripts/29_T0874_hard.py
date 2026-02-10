import socket
import os

def get_local_ip():
    """Find the local IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # Google DNS
    return s.getsockname()[0]

def scan_for_plc():
    """Scan local network for a Rockwell Automation PLC based on open ports (44818 for Ethernet/IP)."""
    local_ip = get_local_ip()
    subnet = ".".join(local_ip.split(".")[:3]) + "."  # Assuming a /24 subnet

    for i in range(1, 255):
        target_ip = subnet + str(i)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((target_ip, 44818))  # Ethernet/IP uses port 44818
            if result == 0:
                print(f"Possible Rockwell PLC found at: {target_ip}")
                sock.close()
                return target_ip
        except Exception as e:
            pass

    return None

plc_ip = scan_for_plc()
if plc_ip:
    print(f"PLC IP Address: {plc_ip}")