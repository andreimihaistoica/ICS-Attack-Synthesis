import scapy.all as scapy
import socket
import struct

# Define the PLC's IP address (will be discovered later)
plc_ip = None

# Define the PLC's port (e.g., Modbus TCP port 1700)
plc_port = 1700

# Define the timeout for the ARP scan
arp_timeout = 2

# Define the operating mode to change to
operating_mode = "Program"  # Replace with the desired operating mode (e.g., "Run", "Remote", "Stop", "Reset", "Test")

# Perform ARP scan to discover the PLC's IP address
def discover_plc_ip():
    global plc_ip
    arp_request = scapy.ARP(pdst="192.168.1.0/24")  # Replace with the subnet of your network
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=arp_timeout, verbose=False)[0]
    for element in answered_list:
        if element[1].psrc == "192.168.1.100":  # Replace with the expected IP address of the PLC
            plc_ip = element[1].psrc
            break

# Connect to the PLC and change the operating mode
def change_operating_mode():
    global plc_ip
    if plc_ip is None:
        print("PLC IP address not found.")
        return

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the PLC
    sock.connect((plc_ip, plc_port))

    # Send a request to the PLC to change the operating mode
    # The request format may vary depending on the PLC's protocol (e.g., Modbus, BACnet, etc.)
    # For example, for Modbus TCP, the request to change the operating mode could be:
    # 0x00 0x00 0x00 0x00 0x00 0x06 0x01 0x01 0x00 0x00 0x00 0x05
    change_mode_request = b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x05"

    # Add the operating mode to the request
    if operating_mode == "Program":
        change_mode_request += b"\x01"
    elif operating_mode == "Run":
        change_mode_request += b"\x02"
    elif operating_mode == "Remote":
        change_mode_request += b"\x03"
    elif operating_mode == "Stop":
        change_mode_request += b"\x04"
    elif operating_mode == "Reset":
        change_mode_request += b"\x05"
    elif operating_mode == "Test":
        change_mode_request += b"\x06"

    # Send the request to the PLC
    sock.send(change_mode_request)

    # Receive the response from the PLC
    response = sock.recv(1024)

    # Check if the operating mode was changed successfully
    if response == b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x05":
        print(f"Operating mode changed to {operating_mode}")
    else:
        print(f"Error changing operating mode to {operating_mode}")

    # Close the socket
    sock.close()

# Call the functions
discover_plc_ip()
change_operating_mode()