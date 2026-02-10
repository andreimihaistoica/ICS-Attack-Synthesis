import os
import time
import socket
from scapy.all import ARP, Ether, srp

# Function to find the PLC's IP address using ARP scanning
def find_plc_ip():
    # Define the IP range to scan (adjust based on your network)
    ip_range = "192.168.1.1/24"
    
    # Create ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Iterate through the responses to find the PLC
    for sent, received in result:
        # Assuming the PLC has a specific MAC address prefix (e.g., 00:1D:9C)
        if received.hwsrc.startswith("00:1D:9C"):
            print(f"Found PLC IP: {received.psrc}")
            return received.psrc

    print("PLC not found in the network.")
    return None

# Function to modify a parameter on the PLC (e.g., motor runtime)
def modify_plc_parameter(plc_ip, parameter, value):
    # Simulate communication with the PLC (replace with actual PLC communication logic)
    print(f"Connecting to PLC at {plc_ip}...")
    time.sleep(1)
    print(f"Modifying parameter '{parameter}' to value: {value}")
    time.sleep(1)
    print("Parameter modified successfully.")

# Main script
if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    
    if plc_ip:
        # Step 2: Modify a critical parameter (e.g., motor runtime)
        parameter = "motor_runtime"
        new_value = 60  # New runtime value in seconds
        modify_plc_parameter(plc_ip, parameter, new_value)
    else:
        print("Unable to proceed without the PLC's IP address.")