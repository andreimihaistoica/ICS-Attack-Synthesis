import snap7
import snap7.client as c
from snap7.util import *
import socket

def find_plc_ip():
    # Broadcast a UDP packet to discover the PLC's IP address
    # This is a simple example and may need adjustments based on the network setup
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)  # Set timeout to 2 seconds
    try:
        sock.sendto(b"DiscoverPLC", ('<broadcast>', 102))  # Port 102 is used by S7 protocol
        response, addr = sock.recvfrom(1024)
        return addr[0]  # Return the IP address of the PLC
    except socket.timeout:
        print("PLC not found on the network.")
        return None
    finally:
        sock.close()

def read_io_image(plc_ip):
    # Connect to the PLC
    plc = c.Client()
    plc.connect(plc_ip, 0, 1)

    if plc.get_connected():
        print(f"Connected to PLC at {plc_ip}")

        # Define the area and size of the input and output image tables
        input_area = snap7.types.S7AreaPE  # Process Inputs
        output_area = snap7.types.S7AreaPA  # Process Outputs
        start_address = 0  # Starting address of the I/O image
        size = 8  # Size of the I/O image in bytes (adjust based on your PLC configuration)

        # Read the input image table
        input_image = plc.read_area(input_area, 0, start_address, size)
        print("Input Image Table:", get_int(input_image, 0))

        # Read the output image table
        output_image = plc.read_area(output_area, 0, start_address, size)
        print("Output Image Table:", get_int(output_image, 0))

        # Disconnect from the PLC
        plc.disconnect()
        print("Disconnected from PLC.")
    else:
        print("Failed to connect to PLC.")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        read_io_image(plc_ip)
    else:
        print("PLC IP address not found. Exiting.")