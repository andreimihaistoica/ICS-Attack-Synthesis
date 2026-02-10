import os
import subprocess
import socket
import time
from scapy.all import *

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Replace with your network subnet
    subnet = "192.168.1.0/24"
    arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet)
    answered, _ = srp(arp_request, timeout=2, verbose=0)
    
    for _, received in answered:
        # Assuming the PLC's MAC address starts with a known prefix
        if received.src.startswith("00:1c:06"):  # Replace with the actual PLC MAC prefix
            return received.psrc
    
    return None

# Function to block reporting messages
def block_reporting_messages(plc_ip):
    # Create a filter to block messages from the PLC
    filter_rule = f"ip src {plc_ip}"
    
    # Use iptables to block the traffic (Linux only)
    try:
        subprocess.run(["iptables", "-A", "INPUT", "-s", plc_ip, "-j", "DROP"], check=True)
        print(f"Blocked reporting messages from {plc_ip}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to block messages: {e}")

# Main script
if __name__ == "__main__":
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        print(f"Discovered PLC IP: {plc_ip}")
        block_reporting_messages(plc_ip)
    else:
        print("PLC IP address could not be discovered.")