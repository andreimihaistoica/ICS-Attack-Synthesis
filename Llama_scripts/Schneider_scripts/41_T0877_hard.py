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

# Define the Modbus address of the I/O Image table
io_image_address = 0x0000  # Replace with the actual address of the I/O Image table

# Define the length of the I/O Image table
io_image_length = 0x100  # Replace with the actual length of the I/O Image table

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

def collect_io_image():
    global plc_ip
    # Use the pymodbus library to access the PLC's memory regions
    from pymodbus.client.sync import ModbusTcpClient
    client = ModbusTcpClient(plc_ip, plc_port)
    # Read the I/O Image table
    response = client.read_holding_registers(io_image_address, io_image_length)
    # Extract the I/O Image state from the response
    io_image_state = response.registers
    return io_image_state

def main():
    global plc_ip
    # Find the PLC's IP address
    find_plc_ip()
    if plc_ip is None:
        print("PLC not found on the network")
        return
    # Collect the I/O Image state
    io_image_state = collect_io_image()
    print("I/O Image state:", io_image_state)

if __name__ == "__main__":
    main()