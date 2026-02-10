from pymodbus.client.sync import ModbusTcpClient
import socket

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

# Function to modify alarm settings
def modify_alarm_settings(client, alarm_address, new_setting):
    # Use the write_register function from pymodbus
    # Note: The address and new_setting might need to be adjusted based on the PLC's memory layout
    client.write_register(alarm_address, new_setting)

# Function to read alarm settings
def read_alarm_settings(client, alarm_address):
    # Use the read_holding_registers function from pymodbus
    # Note: The address might need to be adjusted based on the PLC's memory layout
    result = client.read_holding_registers(alarm_address, 1)
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
            
            # Modify alarm settings
            alarm_address = 0x1000  # Example: Alarm address
            new_setting = 0x0000  # Example: New alarm setting
            modify_alarm_settings(client, alarm_address, new_setting)
            print(f"Modified alarm setting at address {alarm_address} to {new_setting}")
            
            # Read alarm settings
            current_setting = read_alarm_settings(client, alarm_address)
            print(f"Current alarm setting at address {alarm_address}: {current_setting}")
        else:
            print("Failed to find PLC's IP address")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the client
        if 'client' in locals():
            client.close()