import socket
import struct

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

# Define the Modbus address of the parameters
parameters_address = 0x0000  # Replace with the actual address of the parameters

# Define the length of the parameters
parameters_length = 0x100  # Replace with the actual length of the parameters

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

def modify_parameters():
    global plc_ip
    # Use the pymodbus library to access the PLC's memory regions
    from pymodbus.client.sync import ModbusTcpClient
    client = ModbusTcpClient(plc_ip, plc_port)
    # Read the parameters
    response = client.read_holding_registers(parameters_address, parameters_length)
    # Extract the parameters from the response
    parameters = response.registers
    # Modify the parameters
    parameters[0] = 0xFF00  # Modify the first parameter
    # Write the modified parameters back to the PLC
    client.write_registers(parameters_address, parameters)

def main():
    global plc_ip
    # Find the PLC's IP address
    find_plc_ip()
    if plc_ip is None:
        print("PLC not found on the network")
        return
    # Modify the parameters
    modify_parameters()
    print("Parameters modified")

if __name__ == "__main__":
    main()