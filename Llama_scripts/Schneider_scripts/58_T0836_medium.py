from pymodbus.client.sync import ModbusTcpClient
import socket
import time

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

# Function to modify a parameter
def modify_parameter(client, parameter_address, new_value):
    # Use the write_register function from pymodbus
    # Note: The parameter_address and new_value might need to be adjusted based on the PLC's memory layout
    try:
        client.write_register(parameter_address, new_value)
        print(f"Modified parameter at address {parameter_address} to {new_value}")
    except Exception as e:
        print(f"Failed to modify parameter at address {parameter_address}: {e}")

# Function to read a parameter
def read_parameter(client, parameter_address):
    # Use the read_holding_registers function from pymodbus
    # Note: The parameter_address might need to be adjusted based on the PLC's memory layout
    try:
        result = client.read_holding_registers(parameter_address, 1)
        return result.registers[0]
    except Exception as e:
        print(f"Failed to read parameter at address {parameter_address}: {e}")
        return None

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
            
            # Modify a parameter
            parameter_address = 0x1000  # Example: Parameter address
            new_value = 0x1234  # Example: New parameter value
            modify_parameter(client, parameter_address, new_value)
            
            # Read a parameter
            current_value = read_parameter(client, parameter_address)
            if current_value is not None:
                print(f"Current parameter value at address {parameter_address}: {current_value}")
            else:
                print(f"Failed to read parameter at address {parameter_address}")
        else:
            print("Failed to find PLC's IP address")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the client
        if 'client' in locals():
            client.close()