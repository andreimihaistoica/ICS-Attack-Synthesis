import snap7
import snap7.client as c
from snap7.util import *
from snap7.types import *
import socket

def discover_plc_ip():
    """Discover the PLC's IP address on the network."""
    # Replace '192.168.0.1' with your network's broadcast address if different
    broadcast_address = '192.168.0.255'
    port = 102  # Default Siemens S7 port

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)  # Set timeout for responses

    # Send a broadcast message
    sock.sendto(b'DiscoverPLC', (broadcast_address, port))

    try:
        # Receive response
        data, addr = sock.recvfrom(1024)
        return addr[0]  # Return the IP address of the PLC
    except socket.timeout:
        print("PLC not found on the network.")
        return None
    finally:
        sock.close()

def modify_plc_parameter(plc_ip, db_number, start_offset, new_value):
    """Modify a parameter in the PLC's data block."""
    plc = c.Client()
    try:
        # Connect to the PLC
        plc.connect(plc_ip, 0, 1)

        # Read the current value from the data block
        db_data = plc.db_read(db_number, start_offset, 2)  # Assuming a 2-byte integer

        # Print the current value
        current_value = get_int(db_data, 0)
        print(f"Current value in DB{db_number} at offset {start_offset}: {current_value}")

        # Modify the value
        set_int(db_data, 0, new_value)
        plc.db_write(db_number, start_offset, db_data)
        print(f"Modified value to: {new_value}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        plc.disconnect()

if __name__ == "__main__":
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")

        # Modify a parameter in the PLC's data block
        db_number = 1  # Data block number
        start_offset = 0  # Offset in the data block
        new_value = 5000  # New value to set (e.g., motor run time in milliseconds)

        modify_plc_parameter(plc_ip, db_number, start_offset, new_value)
    else:
        print("Could not find PLC. Exiting.")