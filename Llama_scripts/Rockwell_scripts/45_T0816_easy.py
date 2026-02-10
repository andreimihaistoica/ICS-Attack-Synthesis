import scapy.all as scapy
import socket
import struct

# Define the PLC's IP address (will be discovered later)
plc_ip = None

# Define the PLC's port (e.g., Modbus TCP port 1700)
plc_port = 1700

# Define the timeout for the ARP scan
arp_timeout = 2

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

# Connect to the PLC and restart/shutdown the device
def restart_plc():
    global plc_ip
    if plc_ip is None:
        print("PLC IP address not found.")
        return

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the PLC
    sock.connect((plc_ip, plc_port))

    # Send a request to the PLC to restart the device
    # The request format may vary depending on the PLC's protocol (e.g., Modbus, BACnet, etc.)
    # For example, for Modbus TCP, the request to restart the device could be:
    # 0x00 0x00 0x00 0x00 0x00 0x06 0x01 0x01 0x00 0x00 0x00 0x01
    restart_request = b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x01"
    sock.send(restart_request)

    # Receive the response from the PLC
    response = sock.recv(1024)

    # Check if the restart was successful
    if response == b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x01":
        print("PLC restart successful.")
    else:
        print("PLC restart failed.")

    # Close the socket
    sock.close()

def shutdown_plc():
    global plc_ip
    if plc_ip is None:
        print("PLC IP address not found.")
        return

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the PLC
    sock.connect((plc_ip, plc_port))

    # Send a request to the PLC to shutdown the device
    # The request format may vary depending on the PLC's protocol (e.g., Modbus, BACnet, etc.)
    # For example, for Modbus TCP, the request to shutdown the device could be:
    # 0x00 0x00 0x00 0x00 0x00 0x06 0x01 0x01 0x00 0x00 0x00 0x02
    shutdown_request = b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x02"
    sock.send(shutdown_request)

    # Receive the response from the PLC
    response = sock.recv(1024)

    # Check if the shutdown was successful
    if response == b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x02":
        print("PLC shutdown successful.")
    else:
        print("PLC shutdown failed.")

    # Close the socket
    sock.close()

# Call the functions
discover_plc_ip()
restart_plc()
# shutdown_plc()