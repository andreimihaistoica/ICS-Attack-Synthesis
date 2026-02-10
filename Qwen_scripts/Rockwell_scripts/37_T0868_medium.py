import socket
import pycomm3
from pycomm3 import LogixDriver

def discover_plc_ip():
    # Define the broadcast address and port
    broadcast_address = '255.255.255.255'
    port = 44818  # Common port for EtherNet/IP

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    message = b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sock.sendto(message, (broadcast_address, port))

    # Receive the response
    sock.settimeout(5)  # Set a timeout for the response
    try:
        data, addr = sock.recvfrom(1024)
        print(f"PLC found at IP address: {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("No PLC found on the network.")
        return None

def get_plc_operating_mode(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            # Read the operating mode
            operating_mode = plc.get_plc_state()
            print(f"PLC Operating Mode: {operating_mode}")
    except Exception as e:
        print(f"Error reading PLC operating mode: {e}")

def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        get_plc_operating_mode(plc_ip)

if __name__ == "__main__":
    main()