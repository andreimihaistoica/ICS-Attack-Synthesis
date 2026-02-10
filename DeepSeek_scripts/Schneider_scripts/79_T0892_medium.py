import os
import sys
import scapy.all as scapy
from schneider_plc import SchneiderPLC  # Replace with actual library

def discover_plc_ip():
    # Define the network range to scan (adjust as needed)
    network = "192.168.1.0/24"
    print(f"Scanning network {network} for PLC...")

    # Create an ARP request packet
    arp_request = scapy.ARP(pdst=network)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    # Send the packet and receive the response
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    # Parse the response to find the PLC
    plc_ip = None
    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        print(f"Found device: IP={ip}, MAC={mac}")

        # Check if the MAC address matches a Schneider Electric device
        if mac.startswith("00:80:9F"):  # Replace with actual Schneider MAC prefix
            plc_ip = ip
            print(f"Found PLC at IP: {plc_ip}")
            break

    if not plc_ip:
        print("PLC not found on the network.")
        sys.exit(1)

    return plc_ip

def change_plc_credentials(plc_ip, current_user, current_password, new_password):
    print(f"Connecting to PLC at {plc_ip}...")

    # Initialize the PLC connection
    plc = SchneiderPLC(plc_ip, current_user, current_password)

    try:
        # Change the credentials
        plc.change_credentials(current_user, new_password)
        print(f"Credentials for user '{current_user}' changed successfully.")
    except Exception as e:
        print(f"Failed to change credentials: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Replace with actual credentials and new password
    current_user = "admin"
    current_password = "password"
    new_password = "new_password"

    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()

    # Change the PLC credentials
    change_plc_credentials(plc_ip, current_user, current_password, new_password)