import subprocess
import re
import time
from scapy.all import *

# Function to find the PLC's IP address
def find_plc_ip():
    # Use ARP scan to find devices on the network
    arp_scan = subprocess.run(["arp", "-a"], capture_output=True, text=True)
    arp_output = arp_scan.stdout

    # Regular expression to find IP addresses in ARP scan output
    ip_pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")

    # Iterate through the ARP scan results and identify the PLC
    plc_ip = None
    for line in arp_output.splitlines():
        if "PLC" in line or "plc" in line:  # Replace "PLC" with a unique identifier for your PLC
            ip_match = ip_pattern.search(line)
            if ip_match:
                plc_ip = ip_match.group(1)
                break

    if plc_ip:
        print(f"PLC IP Address found: {plc_ip}")
        return plc_ip
    else:
        print("PLC IP Address not found.")
        return None

# Function to block command messages to the PLC
def block_command_messages(plc_ip):
    def packet_callback(packet):
        # Check if the packet is destined for the PLC
        if IP in packet and packet[IP].dst == plc_ip:
            # Drop the packet (block the command message)
            print(f"Blocking command message to PLC: {packet.summary()}")
            return

    # Start sniffing packets destined for the PLC
    print(f"Blocking command messages to PLC at {plc_ip}...")
    sniff(filter=f"dst host {plc_ip}", prn=packet_callback, store=0)

# Main script
if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()

    if plc_ip:
        # Step 2: Block command messages to the PLC
        block_command_messages(plc_ip)
    else:
        print("Unable to proceed without the PLC's IP address.")