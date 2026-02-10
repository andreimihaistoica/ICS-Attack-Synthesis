import snap7
import sys
import time
import nmap
from scapy.all import *

# Default Siemens credentials (example: older S7 PLCs use "Admin" with no password)
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORDS = ["", "admin", "password", "siemens", "changeMe"]  # Expand as needed

# Port used by Siemens PLCs for S7 communication
S7_PROTOCOL_PORT = 102

# Function to scan the local network for Siemens S7 PLCs
def scan_for_plc():
    print("[*] Scanning the network for Siemens S7-1200 PLCs...")
    nm = nmap.PortScanner()
    
    # Adjust the subnet as needed (e.g., 192.168.1.0/24)
    nm.scan(hosts="192.168.1.0/24", arguments="-p 102 --open")

    for host in nm.all_hosts():
        if S7_PROTOCOL_PORT in nm[host]['tcp'] and nm[host]['tcp'][S7_PROTOCOL_PORT]['state'] == 'open':
            print(f"[+] Possible Siemens PLC found at {host}")
            return host
            
    print("[-] No Siemens PLCs found on the network.")
    return None

# Function to attempt authentication using a default username/password
def attempt_login(ip_address):
    print(f"[*] Attempting default credentials on PLC at {ip_address}...")
    
    for password in DEFAULT_PASSWORDS:
        try:
            plc = snap7.client.Client()
            plc.connect(ip_address, 0, 1)  # Rack 0, Slot 1 (default for S7-1200)
            
            if plc.get_connected():
                print(f"[+] SUCCESS: Default credentials worked for {ip_address} using '{DEFAULT_USERNAME}' / '{password}'")
                plc.disconnect()
                return True
        
        except Exception as e:
            print(f"[-] Failed login attempt with '{DEFAULT_USERNAME}' / '{password}' → {str(e)}")

    print("[-] Default credentials did not work.")
    return False

# Main execution flow
def main():
    plc_ip = scan_for_plc()
    
    if not plc_ip:
        print("[-] Exiting: No S7-1200 PLC found.")
        sys.exit(1)

    success = attempt_login(plc_ip)
    
    if success:
        print(f"[+] Potential security issue: PLC at {plc_ip} is using default credentials.")
    else:
        print("[+] No default credentials found. The PLC appears to be secured.")

if __name__ == "__main__":
    main()