import socket
import struct
import re
import subprocess

# --- Configuration ---
# Placeholder for the PLC IP address, will be determined automatically
PLC_IP_ADDRESS = None  # Will be populated by the find_plc_ip() function
# Placeholder for the PLC default port address, change this if your PLC's port address is different
PLC_PORT = 502  # Common Modbus port
# Tag/Point extraction method (modify according to your PLC's protocol/API)
# This example uses a simple Modbus read request to get the first 10 registers.
# You will likely need to tailor this to *your* specific PLC.
START_REGISTER = 0
NUM_REGISTERS = 10
MODBUS_FUNCTION_CODE = 0x03  # Read Holding Registers


# --- Function to find PLC IP Address ---
def find_plc_ip():
    """
    Attempts to find the PLC's IP address by scanning the network.
    This uses `nmap` and requires it to be installed on the system.
    Alternatively, you can provide a different discovery method.
    """
    try:
        # Use nmap to scan for devices on the local network.  Adjust the IP range if needed.
        # For demonstration purposes, scanning the entire subnet.  Consider limiting this
        # to specific known IP ranges where the PLC might reside to reduce scan time.
        # You may need to adjust the `-n` option if reverse DNS resolution causes issues.
        # The `-sn` option is ping scan, which discovers hosts without port scanning.
        # You'll likely need root/admin privileges to run nmap effectively.
        result = subprocess.run(["nmap", "-sn", "192.168.1.0/24"], capture_output=True, text=True)  # Modify IP Range as necessary
        output = result.stdout

        # Regex to find IP addresses in the nmap output
        ip_pattern = r"Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        matches = re.findall(ip_pattern, output)

        if matches:
            print("Found potential PLC IP addresses:")
            for ip in matches:
                print(f"  - {ip}")
            # Let's just pick the first one for now.  A more robust implementation would
            # try connecting to each one and checking if it's the PLC.
            return matches[0] # returns the first IP address discovered.
        else:
            print("No devices found using nmap.  Ensure nmap is installed and configured correctly.")
            return None # returns None if no IP address is found.

    except FileNotFoundError:
        print("nmap is not installed. Please install nmap to use this function.")
        return None
    except Exception as e:
        print(f"Error during IP address discovery: {e}")
        return None

# --- Function to generate Modbus Read Request ---
def generate_modbus_request(start_register, num_registers):
    """
    Generates a Modbus Read Holding Registers request.
    """
    # Transaction Identifier (2 bytes): Arbitrary value
    transaction_id = 0x0001

    # Protocol Identifier (2 bytes): 0 for Modbus/TCP
    protocol_id = 0x0000

    # Length (2 bytes): Length of the remaining part of the message (6 bytes)
    length = 0x0006

    # Unit Identifier (1 byte): Usually 1 (PLC address on the network)
    unit_id = 0x01

    # Function Code (1 byte): 0x03 for Read Holding Registers
    function_code = MODBUS_FUNCTION_CODE

    # Starting Address (2 bytes): Register to start reading from
    starting_address = start_register

    # Quantity of Registers (2 bytes): Number of registers to read
    quantity_of_registers = num_registers

    # Pack the data into a byte string
    request = struct.pack(">HHHBBHH", transaction_id, protocol_id, length, unit_id, function_code, starting_address, quantity_of_registers)
    return request


# --- Function to extract data (PLACEHOLDER - Adapt to your PLC) ---
def extract_tags_and_values(response_data):
    """
    Placeholder function to extract tag names and values from the response data.
    This needs to be adapted to your specific PLC's communication protocol
    and data format.  This example assumes the Modbus response is a series of
    16-bit integers representing the register values.  This is a VERY basic example.
    """
    try:
        # Skip the header (first 9 bytes for Modbus TCP)
        data = response_data[9:]
        # The first byte of the data should be the number of data bytes that follow
        byte_count = data[0]
        register_data = data[1:]

        # Check if the amount of bytes received matches the quantity received from the PLC
        if (byte_count / 2) != NUM_REGISTERS:
            print("Error: Number of received bytes doesn't match the expected registers.")
            return {}

        #Unpack the register values as 16-bit integers
        register_values = struct.unpack(">" + "H" * NUM_REGISTERS, register_data)

        # Create a dictionary to store the tags and values
        tags_and_values = {}
        for i, value in enumerate(register_values):
            tag_name = f"Register_{START_REGISTER + i}"  # Create a tag name
            tags_and_values[tag_name] = value

        return tags_and_values

    except Exception as e:
        print(f"Error extracting tags and values: {e}")
        return {}


# --- Main Script ---
if __name__ == "__main__":

    # 1. Find the PLC IP address
    PLC_IP_ADDRESS = find_plc_ip()
    if not PLC_IP_ADDRESS:
        print("PLC IP address not found.  Exiting.")
        exit(1)

    print(f"Using PLC IP address: {PLC_IP_ADDRESS}")

    # 2. Create a socket and connect to the PLC
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)  # Set a timeout in case the PLC doesn't respond
        client_socket.connect((PLC_IP_ADDRESS, PLC_PORT))
        print(f"Connected to PLC at {PLC_IP_ADDRESS}:{PLC_PORT}")
    except socket.timeout:
        print(f"Connection to {PLC_IP_ADDRESS}:{PLC_PORT} timed out.")
        exit(1)
    except ConnectionRefusedError:
        print(f"Connection refused by {PLC_IP_ADDRESS}:{PLC_PORT}. Is the PLC running and accepting connections on that port?")
        exit(1)
    except Exception as e:
        print(f"Error connecting to PLC: {e}")
        exit(1)

    # 3. Generate the Modbus request
    modbus_request = generate_modbus_request(START_REGISTER, NUM_REGISTERS)

    # 4. Send the request to the PLC
    try:
        client_socket.sendall(modbus_request)
        print("Modbus request sent.")
    except Exception as e:
        print(f"Error sending data: {e}")
        client_socket.close()
        exit(1)

    # 5. Receive the response from the PLC
    try:
        response_data = client_socket.recv(1024)  # Adjust buffer size as needed
        if not response_data:
            print("No data received from PLC.")
            client_socket.close()
            exit(1)
        print("Response received.")
    except socket.timeout:
        print("Timeout waiting for response from PLC.")
        client_socket.close()
        exit(1)
    except Exception as e:
        print(f"Error receiving data: {e}")
        client_socket.close()
        exit(1)

    # 6. Extract tag names and values from the response
    tags_and_values = extract_tags_and_values(response_data)

    # 7. Print the extracted tag names and values
    if tags_and_values:
        print("\nExtracted Tags and Values:")
        for tag, value in tags_and_values.items():
            print(f"  {tag}: {value}")
    else:
        print("No tags and values extracted.")

    # 8. Close the socket
    client_socket.close()
    print("Connection closed.")