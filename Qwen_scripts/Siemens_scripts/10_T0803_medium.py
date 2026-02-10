import nmap
import socket
from scapy.all import *

# Function to discover the PLC's IP address
def discover_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.1.0/24', arguments='-p 102')  # Adjust the subnet and port as needed
    for host in nm.all_hosts():
        if 'tcp' in nm[host] and 102 in nm[host]['tcp']:
            return host
    return None

# Function to block command messages
def block_command_messages(plc_ip):
    def packet_callback(packet):
        if packet.haslayer(TCP) and packet[IP].dst == plc_ip and packet[TCP].dport == 102:
            print(f"Blocked command message to {plc_ip}")
            return

    sniff(filter="tcp and port 102", prn=packet_callback, store=0)

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        block_command_messages(plc_ip)
    else:
        print("PLC IP address not found. Please check the network configuration.")

if __name__ == "__main__":
    main()