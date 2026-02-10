import socket
import struct
from pycomm3 import LogixDriver, S7Client
from pycomm3.exceptions import CommError

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the broadcast address and port
    broadcast_address = '255.255.255.255'
    port = 102  # Standard port for S7 communication

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    discovery_message = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sock.sendto(discovery_message, (broadcast_address, port))

    # Receive the response
    sock.settimeout(5)  # Set a timeout for the response
    try:
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"PLC found at IP address: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("No PLC found on the network.")
        return None

# Function to read the I/O Image state
def read_io_image(plc_ip):
    try:
        # Create a S7Client instance
        client = S7Client()
        client.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 (default for S7-1200)

        # Read the I/O Image state
        input_image = client.read_area(0x81, 0, 0, 100)  # Area 0x81 is the input image, 0 is the start address, 100 is the length
        output_image = client.read_area(0x82, 0, 0, 100)  # Area 0x82 is the output image, 0 is the start address, 100 is the length

        # Convert the raw data to a list of integers
        input_values = [struct.unpack('B', input_image[i:i+1])[0] for i in range(len(input_image))]
        output_values = [struct.unpack('B', output_image[i:i+1])[0] for i in range(len(output_image))]

        print("Input Image State:", input_values)
        print("Output Image State:", output_values)

    except CommError as e:
        print(f"Communication error: {e}")
    finally:
        client.disconnect()

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        read_io_image(plc_ip)

if __name__ == "__main__":
    main()