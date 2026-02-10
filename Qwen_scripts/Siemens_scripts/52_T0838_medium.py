import socket
import struct
from pys7 import S7Client

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    # This is a simple example using a broadcast to find the PLC
    broadcast_ip = '255.255.255.255'
    port = 102  # Default port for S7 communication

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    message = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sock.sendto(message, (broadcast_ip, port))

    # Receive the response
    sock.settimeout(5)  # Set a timeout for the response
    try:
        data, addr = sock.recvfrom(1024)
        print(f"PLC found at IP: {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("No PLC found")
        return None

# Function to modify alarm settings
def modify_alarm_settings(plc_ip):
    # Create a S7 client
    client = S7Client()
    client.connect(plc_ip, 0, 1)  # Connect to the PLC

    # Example: Disable a specific alarm (DB1, DBX0.0)
    db_number = 1
    start_address = 0
    data_type = 'bool'
    value = False  # Disable the alarm

    # Write the value to the PLC
    client.write_area(0x84, db_number, start_address, data_type, value)

    # Close the connection
    client.disconnect()

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        modify_alarm_settings(plc_ip)
    else:
        print("Failed to find the PLC. Exiting.")

if __name__ == "__main__":
    main()