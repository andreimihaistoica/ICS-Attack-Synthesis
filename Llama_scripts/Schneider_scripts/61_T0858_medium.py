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

# Function to change the operating mode of the PLC
def change_operating_mode(client, mode):
    # Use the write_register function from pymodbus
    # Note: The mode might need to be adjusted based on the PLC's memory layout
    # For example, the following modes are commonly used:
    # 0x00: Program mode
    # 0x01: Run mode
    # 0x02: Remote mode
    # 0x03: Stop mode
    # 0x04: Reset mode
    # 0x05: Test/Monitor mode
    if mode == "program":
        client.write_register(0x1000, 0x00)
    elif mode == "run":
        client.write_register(0x1000, 0x01)
    elif mode == "remote":
        client.write_register(0x1000, 0x02)
    elif mode == "stop":
        client.write_register(0x1000, 0x03)
    elif mode == "reset":
        client.write_register(0x1000, 0x04)
    elif mode == "test":
        client.write_register(0x1000, 0x05)
    else:
        print("Invalid mode")

# Function to read the current operating mode of the PLC
def read_operating_mode(client):
    # Use the read_holding_registers function from pymodbus
    # Note: The address might need to be adjusted based on the PLC's memory layout
    result = client.read_holding_registers(0x1000, 1)
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
            
            # Change the operating mode of the PLC
            mode = "program"  # Example: Change to program mode
            change_operating_mode(client, mode)
            print(f"Changed operating mode to {mode}")
            
            # Read the current operating mode of the PLC
            current_mode = read_operating_mode(client)
            if current_mode == 0x00:
                print("Current operating mode: Program")
            elif current_mode == 0x01:
                print("Current operating mode: Run")
            elif current_mode == 0x02:
                print("Current operating mode: Remote")
            elif current_mode == 0x03:
                print("Current operating mode: Stop")
            elif current_mode == 0x04:
                print("Current operating mode: Reset")
            elif current_mode == 0x05:
                print("Current operating mode: Test/Monitor")
            else:
                print("Unknown operating mode")
        else:
            print("Failed to find PLC's IP address")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the client
        if 'client' in locals():
            client.close()