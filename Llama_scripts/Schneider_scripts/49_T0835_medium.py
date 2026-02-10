from pymodbus.client.sync import ModbusTcpClient

# Example IP address of the PLC
plc_ip_address = '192.168.1.100'

# Create a Modbus client
client = ModbusTcpClient(plc_ip_address)

# Assuming you want to override an output coil (for example, coil address 0x0000)
# The address and value (0xFF00 for true, 0x0000 for false) are examples and may need to be adjusted based on your PLC's configuration
def override_output_coil(client, coil_address, value):
    # Use the write_coil function from pymodbus
    # Note: The address might need to be adjusted based on the PLC's memory layout
    client.write_coil(coil_address, value)

# Assuming you want to read an input (for example, input address 0x1000)
# The address is an example and may need to be adjusted based on your PLC's configuration
def read_input(client, input_address):
    # Use the read_discrete_inputs function from pymodbus
    # Note: The address might need to be adjusted based on the PLC's memory layout
    result = client.read_discrete_inputs(input_address, 1)
    return result.bits[0]

# Example usage
if __name__ == "__main__":
    try:
        # Connect to the PLC
        connection = client.connect()
        print(f"Connected to PLC: {connection}")
        
        # Override an output coil
        override_output_coil(client, 0x0000, 0xFF00)  # Example: Set coil at address 0x0000 to True
        
        # Read an input
        input_status = read_input(client, 0x1000)  # Example: Read input at address 0x1000
        print(f"Input status: {input_status}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the client
        client.close()