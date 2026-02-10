import socket
import struct
import re
import os

# Configuration - Consider making these configurable via command line arguments or a config file
# This script assumes a Modbus TCP connection.  Adjust for other protocols as needed.
MODBUS_PORT = 502  # Standard Modbus TCP port

def find_plc_ip():
    """
    Attempts to automatically discover the PLC's IP address on the network.
    This is a basic discovery method and may need to be adapted for specific network configurations.
    It uses nmap and requires it to be installed.  If nmap is not installed, it will return None.
    """
    try:
        import nmap
    except ImportError:
        print("Nmap Python library not installed.  Please install it (pip install python-nmap) or manually provide the PLC IP address.")
        return None

    nm = nmap.PortScanner()
    print("Scanning network for PLC...")
    nm.scan(hosts='192.168.1.0/24', arguments='-p 502')  # Adjust network range and port as needed
    #Note: The above line is highly dependent on network configurations and needs to be modified
    #      according to the user's local configurations. For example, if their network
    #      uses the range 10.0.0.0/24, then it must be specified instead of 192.168.1.0/24
    for host in nm.all_hosts():
        if 'tcp' in nm[host] and MODBUS_PORT in nm[host]['tcp'] and nm[host]['tcp'][MODBUS_PORT]['state'] == 'open':
            print(f"Found PLC at IP address: {host}")
            return host
    print("PLC not found on the network. Please provide the PLC IP address manually.")
    return None


def read_holding_registers(plc_ip, start_address, quantity):
    """
    Reads holding registers from the PLC using Modbus TCP.

    Args:
        plc_ip (str): The IP address of the PLC.
        start_address (int): The starting address of the registers to read.
        quantity (int): The number of registers to read.

    Returns:
        list: A list of register values, or None on error.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  # Set a timeout to prevent hanging

        try:
          s.connect((plc_ip, MODBUS_PORT))
        except socket.timeout:
          print("Connection timed out.  PLC may be unreachable.")
          return None
        except ConnectionRefusedError:
          print("Connection refused. PLC may not be listening on the Modbus port.")
          return None
        except Exception as e:
          print(f"Connection error: {e}")
          return None

        # Modbus TCP PDU (Protocol Data Unit)
        transaction_id = os.urandom(2)  # Unique identifier for the transaction
        protocol_id = b'\x00\x00'  # Modbus protocol ID
        length = struct.pack('>H', 6)  # Length of the remaining message (6 bytes)
        unit_id = b'\x01'  # Slave address (usually 1)
        function_code = b'\x03'  # Read Holding Registers

        # Modbus Data
        starting_address = struct.pack('>H', start_address)
        quantity_of_registers = struct.pack('>H', quantity)

        # Assemble the Modbus TCP ADU (Application Data Unit)
        modbus_adu = transaction_id + protocol_id + length + unit_id + function_code + starting_address + quantity_of_registers

        s.sendall(modbus_adu)

        response = s.recv(1024)  # Adjust buffer size as needed

        s.close()

        # Parse the response
        if len(response) < 9:
            print("Invalid response length.")
            return None

        received_transaction_id = response[0:2]
        received_protocol_id = response[2:4]
        received_length = struct.unpack('>H', response[4:6])[0]
        received_unit_id = response[6]
        received_function_code = response[7]
        byte_count = response[8]
        register_values = []
        for i in range(byte_count // 2):
            register_values.append(struct.unpack('>H', response[9 + (i * 2): 11 + (i * 2)])[0]) #big-endian unsigned short

        if transaction_id != received_transaction_id:
          print("Transaction ID mismatch in response.")
          return None
        if protocol_id != received_protocol_id:
          print("Protocol ID mismatch in response.")
          return None
        # Verify function code (high bit set indicates error)
        if received_function_code & 0x80:
            exception_code = response[8]
            print(f"Modbus Error: Exception Code {exception_code}")
            return None
        if len(register_values) != quantity:
            print("Incorrect number of registers returned.")
            return None

        return register_values


    except socket.error as e:
        print(f"Socket error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def extract_tags_from_comments(plc_program_file):
    """
    Rudimentary tag extraction by scanning for comments. This is highly dependent on the PLC programming environment.
    This is a very basic example and will likely need significant customization.

    Args:
        plc_program_file (str): Path to the PLC program file (e.g., a text file exported from the PLC programming software).

    Returns:
        dict: A dictionary mapping addresses to tag names, or an empty dictionary if no tags are found.
    """
    tags = {}
    try:
        with open(plc_program_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Example:  Look for lines like "// Address: 40001, Tag: MotorSpeed"
                match = re.search(r'// Address: (\d+), Tag: ([\w]+)', line) # Regex needs to be adjusted based on how tags are defined
                if match:
                    address = int(match.group(1)) - 1 #Modbus addresses often start at 1, but read_holding_registers uses 0-based indexing
                    tag = match.group(2)
                    tags[address] = tag
    except FileNotFoundError:
        print(f"PLC program file not found: {plc_program_file}")
        return {}
    except Exception as e:
        print(f"Error processing PLC program file: {e}")
        return {}
    return tags


def main():
    # 1. Find PLC IP Address
    plc_ip = find_plc_ip()
    if not plc_ip:
        plc_ip = input("Enter the PLC IP address manually: ")
        if not plc_ip:
            print("No PLC IP address provided. Exiting.")
            return


    # 2. Tag Identification (This is the hard part and requires PLC-specific knowledge)
    #    - The method for obtaining tags varies greatly depending on the PLC and its programming environment.
    #    - This script provides a very basic example using comments in a PLC program file.  You'll likely need to
    #      modify this section to work with your specific PLC.

    plc_program_file = "plc_program.txt"  # Replace with the actual path to your PLC program file.
    tags = extract_tags_from_comments(plc_program_file)


    # 3. Point Collection (Read data from the PLC and associate it with tags)
    #    - This example reads holding registers.  Adjust as needed for other data types.

    start_address = 40001 - 1 #Modbus addresses often start at 1, but read_holding_registers uses 0-based indexing
    quantity = 10 # Number of registers to read
    data = read_holding_registers(plc_ip, start_address, quantity)

    if data:
        print("Collected Data:")
        for i, value in enumerate(data):
            address = start_address + i
            if address in tags:
                tag = tags[address]
                print(f"Address: {address+1}, Tag: {tag}, Value: {value}") #Printing address as Modbus
            else:
                print(f"Address: {address+1}, Value: {value}")#Printing address as Modbus
    else:
        print("Failed to collect data from PLC.")

if __name__ == "__main__":
    main()