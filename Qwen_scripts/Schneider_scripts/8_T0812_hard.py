import socket
import struct
import time
import requests
from pymodbus.client.sync import ModbusTcpClient

# Default credentials for the Schneider Electric TM221CE16R PLC
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"

# Function to discover the PLC's IP address on the network
def discover_plc_ip():
    # Define the broadcast address and port
    broadcast_address = "192.168.9.255"
    port = 502  # Modbus TCP port

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    message = b'\x00\x01\x00\x00\x00\x06\x01\x03\x00\x00\x00\x01'
    sock.sendto(message, (broadcast_address, port))

    # Receive the response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"PLC found at IP address: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("No PLC found on the network.")
        return None

# Function to connect to the PLC using default credentials
def connect_to_plc(plc_ip):
    # Create a Modbus TCP client
    client = ModbusTcpClient(plc_ip)

    # Connect to the PLC
    if client.connect():
        print(f"Connected to PLC at {plc_ip}")
        return client
    else:
        print(f"Failed to connect to PLC at {plc_ip}")
        return None

# Function to perform actions on the PLC
def perform_actions(client):
    # Example: Read a register
    response = client.read_holding_registers(0, 1, unit=1)
    if response.isError():
        print("Error reading register")
    else:
        print(f"Register value: {response.registers[0]}")

    # Example: Write a register
    client.write_register(0, 1, unit=1)
    print("Wrote value 1 to register 0")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Connect to the PLC using default credentials
        client = connect_to_plc(plc_ip)
        if client:
            # Perform actions on the PLC
            perform_actions(client)
            # Close the connection
            client.close()

if __name__ == "__main__":
    main()