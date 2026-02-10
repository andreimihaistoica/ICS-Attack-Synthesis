import snap7
import socket
from snap7.util import *
from snap7.types import *

def find_plc_ip():
    # This is a simple method to find the PLC's IP address by scanning the local network.
    # This is a placeholder function; in a real scenario, you would use a proper network scanning tool.
    # For example, you could use `nmap` or a custom ARP scan.
    # Here, we assume the PLC's IP is known or manually input.
    plc_ip = input("Enter the PLC's IP address: ")
    return plc_ip

def modify_plc_program(plc_ip):
    # Connect to the PLC
    plc = snap7.client.Client()
    plc.connect(plc_ip, 0, 1)  # IP, Rack, Slot

    # Example: Modify a specific block (e.g., DB1) in the PLC
    db_number = 1  # Data Block number
    start_address = 0  # Start address in the block
    data_length = 10  # Number of bytes to modify

    # Read the existing data block
    original_data = plc.db_read(db_number, start_address, data_length)

    # Modify the data (example: change the first byte to 0xFF)
    modified_data = bytearray(original_data)
    modified_data[0] = 0xFF

    # Write the modified data back to the PLC
    plc.db_write(db_number, start_address, modified_data)

    print(f"Modified DB{db_number} at address {start_address}.")

    # Disconnect from the PLC
    plc.disconnect()

def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()

    # Step 2: Modify the PLC program
    modify_plc_program(plc_ip)

if __name__ == "__main__":
    main()