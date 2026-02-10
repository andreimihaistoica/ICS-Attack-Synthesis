import socket
import pymodbus
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip(subnet='192.168.1.0/24'):
    # Use a simple UDP broadcast to discover the PLC
    broadcast_ip = subnet.split('/')[0].rsplit('.', 1)[0] + '.255'
    port = 502  # Modbus TCP port

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(b'PLC_DISCOVERY', (broadcast_ip, port))

    sock.settimeout(5)  # Wait for 5 seconds for a response
    try:
        data, addr = sock.recvfrom(1024)
        if data == b'PLC_RESPONSE':
            return addr[0]
    except socket.timeout:
        print("No PLC found on the network.")
        return None

# Function to read the I/O Image from the PLC
def read_io_image(plc_ip, start_address, count):
    client = ModbusTcpClient(plc_ip)
    try:
        client.connect()
        if not client.is_socket_open():
            print(f"Failed to connect to PLC at {plc_ip}")
            return None

        # Read the input registers (I/O Image)
        response = client.read_input_registers(start_address, count, unit=1)
        if response.isError():
            print(f"Error reading I/O Image from PLC at {plc_ip}")
            return None

        return response.registers
    finally:
        client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("PLC not found. Exiting.")
        return

    print(f"PLC found at IP address: {plc_ip}")

    # Define the start address and number of registers to read
    start_address = 0  # Example start address
    count = 10         # Example number of registers to read

    # Read the I/O Image
    io_image = read_io_image(plc_ip, start_address, count)
    if io_image:
        print("I/O Image state:")
        for i, value in enumerate(io_image):
            print(f"Register {start_address + i}: {value}")

if __name__ == "__main__":
    main()