import socket
import struct
from pymodbus.client import ModbusTcpClient

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    # This is a simple example using a broadcast to find the PLC
    # In a real-world scenario, you might use a more sophisticated method
    broadcast_ip = '255.255.255.255'
    port = 502  # Modbus TCP port

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    message = b'\x00\x01\x00\x00\x00\x06\x01\x03\x00\x00\x00\x01'
    sock.sendto(message, (broadcast_ip, port))

    # Receive the response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        print(f"PLC found at IP: {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("No PLC found")
        return None

# Function to modify a parameter in the PLC
def modify_plc_parameter(plc_ip, register_address, new_value):
    # Connect to the PLC
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return

    # Convert the new value to the appropriate format (e.g., 16-bit integer)
    value = struct.pack('>H', new_value)

    # Write the new value to the specified register
    result = client.write_register(register_address, new_value)
    if result.isError():
        print(f"Failed to write to register {register_address}")
    else:
        print(f"Successfully modified register {register_address} to {new_value}")

    # Close the connection
    client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        return

    # Define the register address and the new value to write
    register_address = 0x0001  # Example register address
    new_value = 12345  # Example new value

    # Modify the parameter in the PLC
    modify_plc_parameter(plc_ip, register_address, new_value)

if __name__ == "__main__":
    main()