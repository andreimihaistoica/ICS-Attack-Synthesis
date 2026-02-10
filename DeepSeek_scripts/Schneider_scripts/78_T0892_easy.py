import os
import socket
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the IP range to scan (adjust as needed)
    ip_range = "192.168.1.1/24"
    print(f"Scanning network for PLC in range: {ip_range}")

    # Create ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send packet and receive response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse response to find the PLC
    plc_ip = None
    for sent, received in result:
        if "plc" in received.psrc.lower():  # Adjust this condition based on your PLC's hostname or MAC address
            plc_ip = received.psrc
            print(f"Found PLC at IP: {plc_ip}")
            break

    if not plc_ip:
        print("PLC not found in the scanned range.")
    return plc_ip

# Function to change the PLC's credentials
def change_plc_credentials(plc_ip):
    # Simulate changing the PLC's credentials (this is a placeholder)
    # Replace this with actual code to interact with the PLC's API or protocol
    print(f"Changing credentials for PLC at {plc_ip}...")

    # Example: Modify the PLC's password or enable a previously unset key
    # This step depends on the PLC's specific protocol and API
    # For example, using a library like `pymodbus` or `snap7` for Modbus or S7 PLCs

    # Simulate success
    print("Credentials changed successfully. Operators are now locked out.")

# Main script
if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()

    if plc_ip:
        # Step 2: Change the PLC's credentials
        change_plc_credentials(plc_ip)
    else:
        print("Cannot proceed without the PLC's IP address.")