import snap7
import socket
import struct
import time
import subprocess

# --- Configuration ---
# Define the PLC's Rack and Slot
PLC_RACK = 0  # Adjust if needed
PLC_SLOT = 1  # Adjust if needed

# Define the data block and bytes that control the firmware update mode.
# These will vary greatly depending on the specific PLC model and how it's programmed!
DB_NUMBER = 1  # Example:  Data Block 1.  You MUST determine the correct DB.
START_BYTE = 0  # Example: Byte 0 in the DB.  You MUST determine the correct byte.
BYTE_LENGTH = 1 # Number of bytes to read to identify PLC's IP address
FIRMWARE_UPDATE_MODE_ON_VALUE = 1  # Value to write to activate firmware update (e.g., 1 = True, 0 = False)
FIRMWARE_UPDATE_MODE_OFF_VALUE = 0 # Value to write to deactivate firmware update
DELAY_BEFORE_DEACTIVATE = 5  # Time in seconds to wait before deactivating firmware update mode

# S7 Protocol Constants
S7_HEADER_SIZE = 12
S7_READ_VAR_REQ = b'\x11\x04'

# Default PLC IP address (used if discovery fails)
DEFAULT_PLC_IP = "192.168.1.10"  # Replace with a reasonable default for your network

# Function to discover PLC's IP address
def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address using nmap.  This requires nmap to be installed.
    This is a simple discovery method. More sophisticated methods might be necessary for
    complex network configurations.

    Returns:
        str: The PLC's IP address, or None if discovery fails.
    """
    try:
        # Example: Scan the 192.168.1.0/24 network.  Adjust the subnet as needed.
        nmap_result = subprocess.run(['nmap', '-p102', '192.168.1.0/24'], capture_output=True, text=True)  # Port 102 is common for S7

        output = nmap_result.stdout
        #print(output) # debug purposes only

        # Parse the nmap output to find the PLC's IP address. This is a fragile approach!
        # Adapt this parsing logic to match the specific output of your nmap scan.
        for line in output.splitlines():
            if "102/tcp" in line and "open" in line:
                parts = line.split()
                ip_address = parts[0]
                return ip_address
        print("PLC IP address not found.")
        return None  # Not found

    except FileNotFoundError:
        print("Nmap is not installed. Please install nmap to use IP address discovery.")
        return None
    except Exception as e:
        print(f"Error during IP address discovery: {e}")
        return None

def check_plc_ip(ip_address):
    """
    Function to check if a given IP address is valid
    """
    try:
        socket.inet_aton(ip_address)
        return True
    except socket.error:
        return False


def read_plc_ip(client, db_number, start_byte, byte_length):
    """
    Function to read the PLC's IP address from its data block
    """
    try:
        # Read data from the PLC
        data = client.db_read(db_number, start_byte, byte_length)
        # Convert the raw bytes to a string representing an IP address
        # Convert the bytes to a string
        ip_bytes = data[:4]  # Extract the first 4 bytes (assuming IP address is stored as 4 bytes)

        # Convert the bytes to integers
        ip_numbers = struct.unpack('BBBB', ip_bytes)

        # Format the IP address
        ip_address = '.'.join(map(str, ip_numbers))
        return ip_address

    except Exception as e:
        print(f"Error reading PLC IP address: {e}")
        return None

def write_to_plc(client, db_number, start_byte, value):
    """
    Writes a single byte to the specified data block and byte offset in the PLC.
    """
    try:
        # Create a byte array containing the value to write. snap7 requires a byte array.
        data = bytearray([value])  # Convert the integer value into a byte array

        # Write the data to the PLC.
        client.db_write(db_number, start_byte, data)
        print(f"Successfully wrote value {value} to DB{db_number}.DBB{start_byte}")

    except Exception as e:
        print(f"Error writing to PLC: {e}")


def main():
    plc_ip = discover_plc_ip()

    if plc_ip is None or not check_plc_ip(plc_ip):
        print("PLC IP discovery failed. Using default IP:", DEFAULT_PLC_IP)
        plc_ip = DEFAULT_PLC_IP

    # --- PLC Interaction ---
    plc = snap7.client.Client()

    try:
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {plc_ip}")

        # --- Activate Firmware Update Mode ---
        print("Activating Firmware Update Mode...")
        write_to_plc(plc, DB_NUMBER, START_BYTE, FIRMWARE_UPDATE_MODE_ON_VALUE)

        # --- Wait ---
        print(f"Waiting {DELAY_BEFORE_DEACTIVATE} seconds...")
        time.sleep(DELAY_BEFORE_DEACTIVATE)

        # --- Deactivate Firmware Update Mode ---
        print("Deactivating Firmware Update Mode...")
        write_to_plc(plc, DB_NUMBER, START_BYTE, FIRMWARE_UPDATE_MODE_OFF_VALUE)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    main()