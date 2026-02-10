import snap7
import socket
import struct
from snap7.util import *

def discover_plc_ip(network_prefix="192.168.0."):
    """
    Discover the PLC's IP address by scanning the network.
    """
    for i in range(1, 255):
        ip = network_prefix + str(i)
        try:
            # Ping the IP address
            socket.create_connection((ip, 102), timeout=1)
            print(f"Discovered PLC at IP: {ip}")
            return ip
        except:
            continue
    raise Exception("PLC not found on the network.")

def suppress_alarm(plc_ip):
    """
    Suppress alarms by modifying the PLC's memory or flags.
    """
    # Initialize the client
    client = snap7.client.Client()
    client.connect(plc_ip, 0, 1)

    # Example: Suppress alarm by setting a flag in the PLC's memory
    db_number = 1  # Data block number where the alarm flag is located
    start_offset = 0  # Offset of the alarm flag in the data block
    size = 1  # Size of the alarm flag (1 byte)

    # Read the current value of the alarm flag
    data = client.db_read(db_number, start_offset, size)
    current_value = get_bool(data, 0, 0)  # Extract the boolean value

    print(f"Current alarm flag value: {current_value}")

    # Modify the alarm flag to suppress the alarm
    set_bool(data, 0, 0, False)  # Set the flag to False
    client.db_write(db_number, start_offset, data)

    # Verify the change
    updated_data = client.db_read(db_number, start_offset, size)
    updated_value = get_bool(updated_data, 0, 0)
    print(f"Updated alarm flag value: {updated_value}")

    # Disconnect from the PLC
    client.disconnect()

def main():
    try:
        # Discover the PLC's IP address
        plc_ip = discover_plc_ip()
        print(f"PLC IP Address: {plc_ip}")

        # Suppress the alarm
        suppress_alarm(plc_ip)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()