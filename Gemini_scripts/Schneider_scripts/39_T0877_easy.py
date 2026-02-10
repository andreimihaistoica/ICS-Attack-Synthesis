import snap7
import socket
import struct
import time
import os

# Configuration (Modify these based on your PLC and network)
PLC_IP_RANGE = "192.168.1.0/24"  # Example, adjust to your network range
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER = 1  # Example: The Data Block number to read (adjust accordingly)
START_ADDRESS = 0  # Example: Starting address within the DB (adjust accordingly)
BYTE_COUNT = 256  # Example: Number of bytes to read (adjust accordingly)
OUTPUT_FILE = "io_image_capture.bin"


def find_plc_ip(ip_range):
    """
    Scans the network for a PLC by attempting a connection.
    This is a rudimentary scanner and may not be reliable in all networks.
    Consider using a more robust network scanning tool like nmap for production environments.

    Args:
        ip_range: A string representing the IP range to scan (e.g., "192.168.1.0/24").
                  Requires the 'python-nmap' package for subnet calculation.

    Returns:
        The IP address of the PLC if found, otherwise None.
    """
    try:
        import nmap  # Requires: pip install python-nmap
        import ipaddress

        nm = nmap.PortScanner()

        # Convert CIDR notation to a list of individual IP addresses
        ip_network = ipaddress.ip_network(ip_range, strict=False)
        ip_list = [str(ip) for ip in ip_network]

        print(f"Scanning IP range: {ip_range} for PLC...")

        # Scan for port 102 (standard S7 port) - adjust if your PLC uses a different port
        nm.scan(hosts=','.join(ip_list), ports='102', arguments='-T4')

        for host in nm.all_hosts():
            if 'tcp' in nm[host] and 102 in nm[host]['tcp'] and nm[host]['tcp'][102]['state'] == 'open':
                print(f"PLC found at IP address: {host}")
                return host

        print("No PLC found within the specified IP range.")
        return None

    except ImportError:
        print("Error: The 'python-nmap' package is required for IP range scanning.")
        print("Please install it using: pip install python-nmap")
        return None
    except Exception as e:
        print(f"An error occurred during network scanning: {e}")
        return None

def capture_io_image(plc_ip, rack, slot, db_number, start_address, byte_count, output_file):
    """
    Captures the I/O image from a Siemens S7 PLC using the snap7 library.

    Args:
        plc_ip: The IP address of the PLC.
        rack: The PLC rack number.
        slot: The PLC slot number.
        db_number: The Data Block number to read.
        start_address: The starting address within the Data Block.
        byte_count: The number of bytes to read.
        output_file: The name of the file to save the captured data.
    """
    try:
        # Create a Snap7 client
        plc = snap7.client.Client()

        # Connect to the PLC
        plc.connect(plc_ip, rack, slot)
        print(f"Connected to PLC at {plc_ip}, Rack={rack}, Slot={slot}")

        # Read the specified Data Block
        data = plc.db_read(db_number, start_address, byte_count)
        print(f"Read {byte_count} bytes from DB{db_number}, starting at address {start_address}")


        # Save the data to a file
        with open(output_file, "wb") as f:
            f.write(data)
        print(f"I/O image saved to {output_file}")

        # Disconnect from the PLC
        plc.disconnect()
        print("Disconnected from PLC.")

    except snap7.exceptions.Snap7Exception as e:
        print(f"Snap7 error: {e}")
        print("Check PLC connection, rack/slot settings, and DB access permissions.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



if __name__ == "__main__":
    # 1. Find the PLC IP address
    plc_ip_address = find_plc_ip(PLC_IP_RANGE)

    if plc_ip_address:
        # 2. Capture the I/O image
        capture_io_image(plc_ip_address, PLC_RACK, PLC_SLOT, DB_NUMBER, START_ADDRESS, BYTE_COUNT, OUTPUT_FILE)
    else:
        print("PLC IP address not found.  Please check network configuration and IP range.")