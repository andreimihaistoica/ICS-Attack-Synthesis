import snap7
import snap7.client as c
from snap7.util import *
import socket

def find_plc_ip():
    # This is a placeholder function to simulate finding the PLC's IP address.
    # In a real-world scenario, you might use network scanning tools or DHCP logs.
    # For simplicity, we'll assume the PLC's IP is known or provided by the user.
    plc_ip = input("Enter the PLC's IP address: ")
    return plc_ip

def read_io_image(plc_ip):
    try:
        # Create a Snap7 client
        client = c.Client()

        # Connect to the PLC
        client.connect(plc_ip, 0, 1)

        # Read the input image table (assuming it starts at byte 0 with a length of 10 bytes)
        input_image = client.db_read(0, 0, 10)

        # Read the output image table (assuming it starts at byte 10 with a length of 10 bytes)
        output_image = client.db_read(0, 10, 10)

        # Disconnect from the PLC
        client.disconnect()

        return input_image, output_image

    except Exception as e:
        print(f"Error reading I/O Image: {e}")
        return None, None

def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()

    # Read the I/O Image
    input_image, output_image = read_io_image(plc_ip)

    if input_image and output_image:
        print("Input Image Table:")
        print(input_image)

        print("\nOutput Image Table:")
        print(output_image)
    else:
        print("Failed to read the I/O Image.")

if __name__ == "__main__":
    main()