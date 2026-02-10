import snap7
from snap7.util import *
from snap7.types import *

# Function to discover the PLC's IP address (optional, if IP is unknown)
def find_plc_ip():
    # Implement a simple network scan or use a predefined method to find the PLC's IP
    # For simplicity, this example assumes the IP is already known
    plc_ip = "192.168.0.1"  # Replace with the actual IP or implement a discovery method
    return plc_ip

# Function to read the I/O Image from the PLC
def read_io_image(plc):
    # Define the memory areas to read (input and output image tables)
    input_image_size = 128  # Size of the input image table in bytes (adjust based on PLC configuration)
    output_image_size = 128  # Size of the output image table in bytes (adjust based on PLC configuration)

    # Read the input image table
    input_image = plc.read_area(Areas.PE, 0, 0, input_image_size)
    print("Input Image Table:")
    print(input_image)

    # Read the output image table
    output_image = plc.read_area(Areas.PA, 0, 0, output_image_size)
    print("Output Image Table:")
    print(output_image)

    return input_image, output_image

# Main function
def main():
    # Find the PLC's IP address (if not already known)
    plc_ip = find_plc_ip()
    print(f"PLC IP Address: {plc_ip}")

    # Connect to the PLC
    plc = snap7.client.Client()
    plc.connect(plc_ip, 0, 1)  # IP, Rack, Slot

    if plc.get_connected():
        print("Connected to PLC successfully!")
    else:
        print("Failed to connect to PLC. Check the IP address and connection.")
        return

    # Read the I/O Image
    input_image, output_image = read_io_image(plc)

    # Disconnect from the PLC
    plc.disconnect()
    print("Disconnected from PLC.")

if __name__ == "__main__":
    main()