import socket
import struct
from pycomm3 import LogixDriver, S7Client
from pycomm3.s7 import S7AreaDB, S7AreaPE, S7AreaPA, S7AreaTM, S7AreaCT

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the broadcast address and port
    broadcast_address = '255.255.255.255'
    port = 102

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    message = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sock.sendto(message, (broadcast_address, port))

    # Receive the response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        return addr[0]
    except socket.timeout:
        print("No PLC found on the network.")
        return None

# Function to read the I/O Image
def read_io_image(plc_ip):
    try:
        # Connect to the PLC
        plc = S7Client()
        plc.connect(plc_ip, 0, 1)

        # Define the memory regions to read
        input_image = S7AreaPE
        output_image = S7AreaPA

        # Read the input image (e.g., %I0.0 to %I0.7)
        input_data = plc.read_area(input_image, 0, 0, 1)
        input_values = struct.unpack('B', input_data)[0]

        # Read the output image (e.g., %Q0.0 to %Q0.7)
        output_data = plc.read_area(output_image, 0, 0, 1)
        output_values = struct.unpack('B', output_data)[0]

        # Print the input and output values
        print(f"Input Image: {bin(input_values)}")
        print(f"Output Image: {bin(output_values)}")

        # Close the connection
        plc.disconnect()
    except Exception as e:
        print(f"Error reading I/O Image: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        # Read the I/O Image
        read_io_image(plc_ip)
    else:
        print("Failed to discover the PLC's IP address.")

if __name__ == "__main__":
    main()