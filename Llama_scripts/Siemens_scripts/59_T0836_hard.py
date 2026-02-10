import scapy.all as scapy
import socket
import struct

# Define the PLC's IP address (will be discovered later)
plc_ip = None

# Define the PLC's port (e.g., Modbus TCP port 1700)
plc_port = 1700

# Define the timeout for the ARP scan
arp_timeout = 2

# Define the parameter to modify
parameter_name = "Motor_Temp"  # Replace with the desired parameter name
parameter_value = 350  # Replace with the desired parameter value

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

# Connect to the PLC and modify the parameter
def modify_parameter():
    global plc_ip
    if plc_ip is None:
        print("PLC IP address not found.")
        return

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the PLC
    sock.connect((plc_ip, plc_port))

    # Send a request to the PLC to read the parameter
    # The request format may vary depending on the PLC's protocol (e.g., Modbus, BACnet, etc.)
    # For example, for Modbus TCP, the request to read the parameter could be:
    # 0x00 0x00 0x00 0x00 0x00 0x06 0x01 0x01 0x00 0x00 0x00 0x03
    read_request = b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x03"

    # Send the request to the PLC
    sock.send(read_request)

    # Receive the response from the PLC
    response = sock.recv(1024)

    # Parse the response to extract the parameter value
    # The parsing logic may vary depending on the PLC's protocol and response format
    parameter_value_current = struct.unpack(">H", response[10:12])[0]

    # Modify the parameter value
    parameter_value_new = parameter_value

    # Send a request to the PLC to write the modified parameter value
    # The request format may vary depending on the PLC's protocol (e.g., Modbus, BACnet, etc.)
    # For example, for Modbus TCP, the request to write the parameter value could be:
    # 0x00 0x00 0x00 0x00 0x00 0x06 0x01 0x01 0x00 0x00 0x00 0x04
    write_request = b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x04"
    write_request += struct.pack(">H", parameter_value_new)

    # Send the request to the PLC
    sock.send(write_request)

    # Receive the response from the PLC
    response = sock.recv(1024)

    # Check if the write was successful
    if response == b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x04":
        print(f"Parameter {parameter_name} modified to {parameter_value_new}")
    else:
        print(f"Error modifying parameter {parameter_name}")

    # Close the socket
    sock.close()

# Call the functions
discover_plc_ip()
modify_parameter()