from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

def find_plc_ip():
    # Implement a method to find the PLC's IP address on the network.
    # This could be done using ARP scanning, network discovery, or other methods.
    # For simplicity, we assume the IP is known or provided.
    return "192.168.9.24"

def collect_io_image(plc_ip):
    # Connect to the PLC
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print("Failed to connect to the PLC.")
        return

    # Define the memory regions to read (input and output image tables)
    input_start_address = 0x0000  # Start address for input image table
    input_length = 16              # Number of input registers to read

    output_start_address = 0x1000  # Start address for output image table
    output_length = 16              # Number of output registers to read

    try:
        # Read the input image table
        input_response = client.read_holding_registers(input_start_address, input_length, unit=1)
        if input_response.isError():
            print("Failed to read input image table.")
            return

        # Decode the input registers
        input_decoder = BinaryPayloadDecoder.fromRegisters(input_response.registers, byteorder=Endian.Big)
        input_image = [input_decoder.decode_16bit_int() for _ in range(input_length)]

        # Read the output image table
        output_response = client.read_holding_registers(output_start_address, output_length, unit=1)
        if output_response.isError():
            print("Failed to read output image table.")
            return

        # Decode the output registers
        output_decoder = BinaryPayloadDecoder.fromRegisters(output_response.registers, byteorder=Endian.Big)
        output_image = [output_decoder.decode_16bit_int() for _ in range(output_length)]

        # Print the collected I/O image
        print("Input Image Table:", input_image)
        print("Output Image Table:", output_image)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        client.close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC IP Address found: {plc_ip}")
        collect_io_image(plc_ip)
    else:
        print("PLC IP Address could not be determined.")