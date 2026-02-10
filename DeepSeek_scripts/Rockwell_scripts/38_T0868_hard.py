import socket
import struct
from ctypes import *

# Define the PLC's IP address (manually set or discovered via network scan)
PLC_IP = "192.168.1.10"  # Replace with the actual IP address or use a discovery method
PLC_PORT = 44818  # Default Ethernet/IP port for Rockwell PLCs

# Define the CIP (Common Industrial Protocol) message to detect the operating mode
CIP_OPERATING_MODE_REQUEST = bytes([
    0x6F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
])

def discover_plc_ip():
    # Placeholder for network scan logic to discover the PLC's IP address
    # Use tools like nmap or ARP scanning to find the PLC on the network
    print("Implement PLC IP discovery logic here...")
    return "192.168.1.10"  # Replace with dynamic discovery logic

def detect_operating_mode(ip, port):
    try:
        # Create a socket connection to the PLC
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((ip, port))

        # Send the CIP request to detect the operating mode
        sock.send(CIP_OPERATING_MODE_REQUEST)

        # Receive the response
        response = sock.recv(1024)
        sock.close()

        # Parse the response to determine the operating mode
        if len(response) >= 4:
            mode_byte = response[3]  # The operating mode is often encoded in the response
            if mode_byte == 0x00:
                return "Run"
            elif mode_byte == 0x01:
                return "Program"
            elif mode_byte == 0x02:
                return "Remote"
            elif mode_byte == 0x03:
                return "Stop"
            elif mode_byte == 0x04:
                return "Reset"
            elif mode_byte == 0x05:
                return "Test/Monitor"
            else:
                return f"Unknown Mode: {mode_byte}"
        else:
            return "Invalid response from PLC"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address (if not manually set)
    PLC_IP = discover_plc_ip()
    print(f"PLC IP Address: {PLC_IP}")

    # Step 2: Detect the PLC's operating mode
    operating_mode = detect_operating_mode(PLC_IP, PLC_PORT)
    print(f"PLC Operating Mode: {operating_mode}")