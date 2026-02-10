from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient
import socket

# Common default credentials for PLCs (example: change these as needed)
DEFAULT_CREDENTIALS = [
    ("admin", "admin"),
    ("user", "user"),
    ("guest", "guest"),
    ("root", "root")
]

# Define network scanning function to identify the PLC's IP
def find_plc_ip(network_range="192.168.1.0/24", target_port=502):
    print("[*] Scanning the network for PLC devices...")
    
    ans, _ = srp(
        Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range),
        timeout=2, verbose=False
    )

    # Go through responses to check for PLCs
    for _, rcv in ans:
        ip = rcv.psrc
        # Check if the IP has port 502 open (common for Modbus devices)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        result = sock.connect_ex((ip, target_port))
        sock.close()

        if result == 0:  # Port 502 open
            print(f"[*] Potential PLC detected at {ip}")
            return ip

    print("[!] No PLCs detected on network.")
    return None

# Function to attempt login to PLC using known default credentials
def try_default_credentials(plc_ip):
    print(f"[*] Attempting to log in using default credentials on PLC at {plc_ip}...")

    for username, password in DEFAULT_CREDENTIALS:
        try:
            plc_client = ModbusClient(host=plc_ip, port=502, auto_open=True)

            if plc_client.open():
                print(f"[+] Success! Default credentials ({username}/{password}) worked on {plc_ip}")
                plc_client.close()
                return True
            else:
                print(f"[-] Failed to authenticate with {username}/{password}")

        except Exception as e:
            print(f"[!] Error attempting login: {e}")

    print("[!] No default credentials worked.")
    return False

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        try_default_credentials(plc_ip)