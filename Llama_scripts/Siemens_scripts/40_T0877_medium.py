import socket
import random
from pyopcuapy import client
import snap7

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same network as the Windows machine
    # and the subnet mask is 255.255.255.0
    for i in range(1, 255):
        ip = f"192.168.1.{i}"
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ip, 102))
            client.close()
            return ip
        except ConnectionRefusedError:
            pass
    return None

# Function to collect the I/O Image state of the PLC
def collect_io_image(plc_ip):
    # Create a S7 client object
    s7_client = snap7.S7Client()

    # Connect to the S7 server
    s7_client.ConnectTo(plc_ip, 0, 1)

    # Read the input image table
    input_image = s7_client.ReadArea(snap7.s7const.S7AreaPE, 0, 0)

    # Print the input image table
    print("Input Image Table:")
    print(input_image)

    # Read the output image table
    output_image = s7_client.ReadArea(snap7.s7const.S7AreaPA, 0, 0)

    # Print the output image table
    print("Output Image Table:")
    print(output_image)

    # Disconnect from the S7 server
    s7_client.Disconnect()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        collect_io_image(plc_ip)
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()