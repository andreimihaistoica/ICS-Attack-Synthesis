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

# Function to perform a program download on the PLC
def program_download(client, program_name, program_data):
    # Use the write_register function from pymodbus
    # Note: The program_name and program_data might need to be adjusted based on the PLC's memory layout
    try:
        # Get the current program
        current_program = client.read_holding_registers(0x1000, 100)
        current_program = current_program.registers
        
        # Modify the program
        modified_program = current_program
        for i, instruction in enumerate(program_data):
            modified_program[i] = instruction
        
        # Write the modified program to the PLC
        client.write_registers(0x1000, modified_program)
        print(f"Performed program download of {program_name} on PLC")
    except Exception as e:
        print(f"Failed to perform program download of {program_name} on PLC: {e}")

# Function to read a program on the PLC
def read_program(client, program_name):
    # Use the read_holding_registers function from pymodbus
    # Note: The program_name might need to be adjusted based on the PLC's memory layout
    try:
        # Get the current program
        current_program = client.read_holding_registers(0x1000, 100)
        current_program = current_program.registers
        print(f"Current program {program_name} on PLC: {current_program}")
    except Exception as e:
        print(f"Failed to read program {program_name} on PLC: {e}")

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
            
            # Perform a program download on the PLC
            program_name = "MainProgram"
            program_data = [0x01, 0x02, 0x03, 0x04, 0x05]
            program_download(client, program_name, program_data)
            
            # Read a program on the PLC
            read_program(client, program_name)
        else:
            print("Failed to find PLC's IP address")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the client
        if 'client' in locals():
            client.close()