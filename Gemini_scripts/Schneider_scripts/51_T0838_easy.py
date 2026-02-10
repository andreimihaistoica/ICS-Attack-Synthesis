import snap7
import time
import socket
import struct

# Configuration
PLC_IP = None  # Initially unknown, will be discovered
PLC_RACK = 0  # Typically 0 for S7-300/400
PLC_SLOT = 1  # Typically 1 for S7-300/400 CPU

DB_NUMBER = 1  # Example Data Block number, adjust to your PLC program
ALARM_SETTINGS_OFFSET = 0  # Offset within the DB where alarm settings are located.  Adjust!
ALARM_SETTINGS_LENGTH = 4 # Length of the alarm settings data in bytes.  Adjust!

# Target alarm ID to disable (example)
TARGET_ALARM_ID = 1234 # Example, should be a real alarm ID

# Value to disable the alarm (example, could be a bitmask or specific value)
DISABLE_VALUE = 0  # This will depend on how the alarm is enabled/disabled

# Function to discover the PLC's IP address by broadcasting a request
def discover_plc_ip():
    """
    Discovers the PLC's IP address by sending a broadcast UDP packet and listening for a response.
    This assumes the PLC is configured to respond to such requests.  This is a very basic example.
    A more robust discovery method might involve reading PLC configuration files or using a dedicated discovery protocol.
    """
    broadcast_address = '<broadcast>'  # Assumes same network. Adjust if needed
    broadcast_port = 1616  #Example broadcast port, can be changed
    request_message = b"PLC_DISCOVERY"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5) # Set a timeout for receiving a response

    try:
        sock.sendto(request_message, (broadcast_address, broadcast_port))
        print("Sent broadcast request for PLC IP.")

        data, addr = sock.recvfrom(1024)  # Buffer size
        plc_ip = addr[0]
        print(f"Received response from: {plc_ip}")
        return plc_ip

    except socket.timeout:
        print("No PLC response received within the timeout period.")
        return None
    except Exception as e:
        print(f"An error occurred during discovery: {e}")
        return None

    finally:
        sock.close()


def modify_alarm_settings(plc_ip, db_number, offset, length, new_value):
    """
    Modifies alarm settings in the specified Data Block of the PLC.

    Args:
        plc_ip (str): IP address of the PLC.
        db_number (int): Data Block number.
        offset (int): Offset within the DB.
        length (int): Length of the data to write (in bytes).
        new_value (int): The new integer value to write.  Assumes you are writing an integer.
                       Adjust data type handling as needed.
    """
    try:
        # Initialize the Snap7 client
        plc = snap7.client.Client()
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {plc_ip}")

        # Read the current value from the PLC
        current_data = plc.db_read(db_number, offset, length)
        current_value = struct.unpack('>i', current_data)[0] # Assuming an integer, adjust as needed.
        print(f"Current Alarm Settings value: {current_value}")

        # Prepare the new data
        new_data = struct.pack('>i', new_value) # pack as big-endian integer, adjust as needed.


        # Write the new value to the PLC
        plc.db_write(db_number, offset, new_data)
        print(f"Successfully wrote new value {new_value} to DB{db_number}.DBB{offset}")

        # Verify the write (optional, but good practice)
        verify_data = plc.db_read(db_number, offset, length)
        verify_value = struct.unpack('>i', verify_data)[0] # Assuming an integer, adjust as needed.

        if verify_value == new_value:
            print("Write verified successfully.")
        else:
            print(f"WARNING: Write verification failed!  Expected {new_value}, got {verify_value}")

    except snap7.exceptions.Snap7Exception as e:
        print(f"Snap7 Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Disconnect from the PLC
        if 'plc' in locals() and plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")



if __name__ == "__main__":
    # 1. Discover the PLC IP address
    PLC_IP = discover_plc_ip()

    if PLC_IP is None:
        print("PLC IP address discovery failed.  Exiting.")
        exit()

    # 2. Modify the alarm settings
    print("Attempting to modify alarm settings...")
    modify_alarm_settings(PLC_IP, DB_NUMBER, ALARM_SETTINGS_OFFSET, ALARM_SETTINGS_LENGTH, DISABLE_VALUE)

    print("Script completed.")