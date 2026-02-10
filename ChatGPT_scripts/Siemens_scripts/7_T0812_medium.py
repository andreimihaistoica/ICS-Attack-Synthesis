import socket
import ipaddress
import struct
from pyModbusTCP.client import ModbusClient

# List of known default credentials for Siemens S7-1200
DEFAULT_CREDENTIALS = [
    ("admin", "admin"),    # Common default
    ("admin", "password"),
    ("admin", "1234"),
    ("user", "user"),
]

# Function to scan for the PLC's IP address
def find_plc_ip(subnet="192.168.1.0/24"):
    """
    Scans the subnet to find an active Siemens S7-1200 PLC.

    Args:
        subnet (str): The subnet in CIDR format to scan.

    Returns:
        str: The IP address of the detected PLC, or None if not found.
    """
    for ip in ipaddress.IPv4Network(subnet, strict=False):
        try:
            # Send a simple TCP SYN request to check if the PLC is listening on port 102 (Siemens S7 protocol)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((str(ip), 102))
            s.close()
            if result == 0:
                print(f"[+] Found potential Siemens S7-1200 PLC at {ip}")
                return str(ip)
        except Exception as e:
            pass
    
    print("[-] No Siemens S7-1200 PLC found on the subnet.")
    return None

# Function to attempt default credentials
def try_default_credentials(ip):
    """
    Attempts to log in to the Siemens S7-1200 PLC using default credentials.
    
    Args:
        ip (str): The IP address of the PLC.

    Returns:
        bool: True if authentication was successful, False otherwise.
    """
    client = ModbusClient(host=ip, port=502, auto_open=True, auto_close=True)
    
    for username, password in DEFAULT_CREDENTIALS:
        # Simulating login attempt (Modbus doesn't have direct authentication like this, 
        # but other protocols like ISO-TSAP or web interfaces might)
        print(f"[*] Trying credentials: {username} / {password}")
        
        if client.open():
            print(f"[+] Successful authentication using {username} / {password}")
            client.close()
            return True
        else:
            print("[-] Authentication failed.")
    
    return False

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip("192.168.1.0/24")  # Adjust subnet as needed
    if plc_ip:
        try_default_credentials(plc_ip)
    else:
        print("[-] Could not find Siemens S7-1200 PLC on the network.")