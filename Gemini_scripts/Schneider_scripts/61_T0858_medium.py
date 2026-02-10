import socket
import struct
import time
import re  # For IP address validation

# Configuration - These should ideally be command-line arguments or in a config file
PLC_IP = None  # Determined dynamically
PLC_PORT = 502  # Standard Modbus port (Schneider PLCs often use Modbus)
MODBUS_UNIT_ID = 255  # Unit ID for the PLC (check your PLC configuration)
# Function codes for Modbus (Schneider might deviate - check documentation)
READ_HOLDING_REGISTERS = 0x03
WRITE_SINGLE_REGISTER = 0x06
# Register Addresses (Crucial -  FIND THESE IN YOUR PLC'S MANUAL. These are EXAMPLES.)
#  The addresses below are crucial and WILL LIKELY NEED TO BE CHANGED.
#  Schneider documentation is *essential* to finding the correct register addresses
OPERATING_MODE_REGISTER = 40001  # Example address. Check your PLC manual! Modbus addresses start at 40001 (holding register)
PROGRAM_MODE_VALUE = 1      # Example:  Value to write for Program Mode. Check your PLC manual!
RUN_MODE_VALUE = 2          # Example: Value to write for Run Mode. Check your PLC manual!
STOP_MODE_VALUE = 3        # Example: Value to write for Stop Mode. Check your PLC manual!
REMOTE_MODE_VALUE = 4 # Example: Value to write for Remote Mode. Check your PLC manual!

# Function to validate IP address format
def is_valid_ip(ip_address):
    """
    Checks if the provided string is a valid IPv4 address.
    """
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip_address):
        return False
    octets = ip_address.split('.')
    for octet in octets:
        if int(octet) > 255:
            return False
    return True

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address on the local network.

    This is a rudimentary approach.  In a real-world scenario, a more robust discovery
    method (e.g., using specific PLC discovery protocols) would be necessary.  This assumes
    the PLC responds to simple pings.  It iterates through a subnet, which may not be suitable
    for all networks.

    IMPORTANT:  Adjust the subnet range (e.g., 192.168.1) to match your network configuration.
    """
    subnet = "192.168.1"  # **CHANGE THIS TO YOUR NETWORK'S SUBNET**
    print(f"Attempting to discover PLC IP address on subnet: {subnet}.x")
    for i in range(1, 255):  # Check IPs 192.168.1.1 to 192.168.1.254
        ip = f"{subnet}.{i}"
        try:
            socket.inet_aton(ip) #validate the IP
        except socket.error:
            continue #invalid IP
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1) # short timeout
            result = sock.connect_ex((ip, PLC_PORT))  # Use connect_ex for non-blocking
            if result == 0: #Connects
                print(f"PLC found at IP address: {ip}")
                return ip
            sock.close()
        except socket.error as e:
             # Handle connection errors if needed.
            pass #Timeout or other issues
    print("PLC IP address not found on the subnet.  Please ensure the PLC is on the same network.")
    return None

def modbus_tcp_request(ip_address, port, unit_id, function_code, register_address, register_value=None):
    """
    Generic function to send Modbus TCP requests.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Increased timeout for reliability
        sock.connect((ip_address, port))

        # Build Modbus TCP ADU (Application Data Unit)
        transaction_id = 0  # You can increment this for each request
        protocol_id = 0
        length = 6  # Minimum length for a read request

        if register_value is not None:  # Write request
            length += 2  # Add 2 bytes for the register value
            payload = struct.pack(">BBH", unit_id, function_code, register_address -1) + struct.pack(">H", register_value) # register addresses -1 as the modbus addressing starts at zero
        else:  # Read request
            quantity = 1  # Number of registers to read (usually 1 for this purpose)
            payload = struct.pack(">BBHH", unit_id, function_code, register_address-1, quantity) # register addresses -1 as the modbus addressing starts at zero

        header = struct.pack(">HHH", transaction_id, protocol_id, length)
        adu = header + payload

        sock.sendall(adu)

        response = sock.recv(1024)  # Receive response

        sock.close()

        # Process the response (very basic error checking)
        if response:
            # You need to decode the Modbus response according to the function code.
            # This is a minimal check for errors. Real error handling requires parsing
            # the exception code in the response.
            if response[7] >= 0x80:  # Exception code (function code + 0x80) indicates an error
                print(f"Modbus error: Exception Code {response[8]}")
                return None  # Indicate an error

            return response
        else:
            print("No response from PLC.")
            return None

    except socket.error as e:
        print(f"Socket error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def change_plc_mode(ip_address, target_mode):
    """
    Changes the PLC's operating mode.

    Args:
        ip_address: The IP address of the PLC.
        target_mode:  A string representing the desired mode ('program', 'run', 'stop', 'remote').
    """

    if not is_valid_ip(ip_address):
      print(f"Invalid IP address: {ip_address}")
      return

    mode_value = None
    if target_mode == 'program':
        mode_value = PROGRAM_MODE_VALUE
    elif target_mode == 'run':
        mode_value = RUN_MODE_VALUE
    elif target_mode == 'stop':
        mode_value = STOP_MODE_VALUE
    elif target_mode == 'remote':
        mode_value = REMOTE_MODE_VALUE
    else:
        print(f"Invalid target mode: {target_mode}")
        return

    if mode_value is None:
        print("Invalid mode value")
        return


    # Check current mode first (optional but recommended)
    response = modbus_tcp_request(ip_address, PLC_PORT, MODBUS_UNIT_ID, READ_HOLDING_REGISTERS, OPERATING_MODE_REGISTER)
    if response:
        # Minimal example of reading the register. You'll need to unpack the bytes correctly based on Modbus spec.
        current_mode_value = struct.unpack(">H", response[9:11])[0] #Unpacks the data
        print(f"Current PLC mode value: {current_mode_value}")
    else:
        print("Failed to read current PLC mode.  Aborting mode change.")
        return

    print(f"Attempting to set PLC to {target_mode} mode (value: {mode_value})")
    response = modbus_tcp_request(ip_address, PLC_PORT, MODBUS_UNIT_ID, WRITE_SINGLE_REGISTER, OPERATING_MODE_REGISTER, mode_value)

    if response:
        print(f"PLC mode change to {target_mode} attempted. Check PLC to confirm.")
        # Consider adding a read-back verification here.
    else:
        print(f"Failed to change PLC mode to {target_mode}.")


# --- Main execution ---
if __name__ == "__main__":
    # 1. Find the PLC IP address
    PLC_IP = find_plc_ip()

    if not PLC_IP:
        print("Could not determine PLC IP address. Exiting.")
        exit(1)

    # 2.  Choose the target mode (e.g., 'program', 'run', 'stop')
    target_mode = 'program'  # **CHANGE THIS TO THE DESIRED MODE**

    # 3. Change the PLC mode
    change_plc_mode(PLC_IP, target_mode)