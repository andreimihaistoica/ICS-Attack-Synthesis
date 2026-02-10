import socket
import pycomm3
from pycomm3 import LogixDriver

def find_plc_ip():
    # Define the broadcast address and port
    broadcast_address = '255.255.255.255'
    port = 102  # Default port for S7 communication

    # Create a socket for broadcasting
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to find the PLC
    sock.sendto(b'Hello, PLC!', (broadcast_address, port))

    # Set a timeout for receiving responses
    sock.settimeout(5)

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            if data:
                print(f"PLC found at IP: {addr[0]}")
                return addr[0]
    except socket.timeout:
        print("No PLC found.")
        return None

# Find the PLC's IP address
plc_ip = find_plc_ip()
if plc_ip:
    print(f"PLC IP address: {plc_ip}")
else:
    print("Failed to find the PLC.")