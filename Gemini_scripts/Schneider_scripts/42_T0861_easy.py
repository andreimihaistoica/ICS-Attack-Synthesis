import snap7  # Python wrapper for Siemens S7 communication
import socket  # For network operations and IP address discovery
import re       # For regular expressions (parsing PLC config)
import os       # For running command line tools (ping)

# Configuration (will be dynamically discovered if possible)
PLC_IP_ADDRESS = None  # Discovered automatically
PLC_RACK = 0
PLC_SLOT = 1  # Adjust as needed for your PLC configuration
DB_NUMBER = 1   # Adjust based on where tags/points are stored
START_ADDRESS = 0  # Starting byte address within the DB
BYTE_COUNT = 1024  # Number of bytes to read (adjust as needed)


def find_plc_ip_address():
    """
    Attempts to discover the PLC's IP address by pinging the network.
    Relies on the engineering workstation and PLC being on the same subnet.

    It scans IP addresses in the local subnet, attempting to ping likely candidates.  If it finds
    a PLC that responds to pings, it attempts to connect to it briefly to confirm it's an S7 device.

    Returns:
        str: The IP address of the PLC if found, otherwise None.
    """
    try:
        # Get the local machine's IP address and subnet mask
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        # Extract the network address from the IP address
        ip_parts = local_ip.split('.')
        network_address = '.'.join(ip_parts[:3]) + '.'

        # Scan a range of IP addresses in the local subnet
        for i in range(1, 255):  # Scan from .1 to .254
            target_ip = network_address + str(i)

            # Ping the target IP address
            response = os.system("ping -n 1 -w 500 " + target_ip + " > nul 2>&1")  # Windows ping

            if response == 0:  # Ping successful
                print(f"Ping successful for {target_ip}")

                # Attempt a brief connection to confirm it's an S7 PLC
                try:
                    plc = snap7.client.Client()
                    plc.connect(target_ip, PLC_RACK, PLC_SLOT)
                    print(f"Successfully connected to PLC at {target_ip}.  Assuming this is the PLC's IP.")
                    plc.disconnect()  # Disconnect immediately
                    return target_ip  # Found the PLC
                except snap7.exceptions.Snap7Exception as e:
                    print(f"Connection to {target_ip} failed. Likely not an S7 PLC.")
                    print(f"Error: {e}") #print the error to diagnose further
                except Exception as e:
                    print(f"Unexpected error connecting to {target_ip}: {e}")


    except Exception as e:
        print(f"Error during IP address discovery: {e}")
        return None

    print("PLC IP address discovery failed.  Could not find a PLC on the local network.")
    return None




def collect_points_and_tags(ip_address, rack, slot, db_number, start_address, byte_count):
    """
    Connects to the PLC, reads data from the specified DB, and attempts to
    extract point and tag information.  This is a simplified approach and
    relies on a specific data structure within the PLC's DB.  In reality, the
    structure of the data and how tags are associated with points can be
    very complex and PLC-specific.

    Args:
        ip_address (str): The IP address of the PLC.
        rack (int): The PLC rack number.
        slot (int): The PLC slot number.
        db_number (int): The data block number to read.
        start_address (int): The starting byte address within the DB.
        byte_count (int): The number of bytes to read.

    Returns:
        dict: A dictionary of points and their (potential) associated tags.
               The structure is simplified for this example.  A real-world
               implementation would require understanding the specific
               PLC's data structures.  Returns None on failure.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(ip_address, rack, slot)
        print(f"Connected to PLC at {ip_address}, Rack: {rack}, Slot: {slot}")

        # Read the data block
        data = plc.db_read(db_number, start_address, byte_count)
        print(f"Read {byte_count} bytes from DB{db_number}, starting at byte {start_address}")

        # **IMPORTANT:** This part of the code depends entirely on how the data
        # is structured in your PLC's data block.  This is a *VERY* simplified
        # example.  You will need to adapt this to match the actual data layout.
        #
        # This example assumes that the data block contains:
        # - Strings (likely for tags)
        # - Floating-point numbers (likely for process values)
        # - Integers (likely for status or control values)

        points_and_tags = {}
        offset = 0  # Keep track of the current position in the byte array

        # **ADAPT THIS LOOP TO MATCH YOUR PLC'S DATA STRUCTURE**
        while offset < byte_count:
            # Try to read a tag (assuming it's a string, e.g., 32 bytes)
            tag_length = 32 # Example: Adjust as needed.  Check the DB structure!
            if offset + tag_length <= byte_count:
                tag_bytes = data[offset:offset + tag_length]
                try:
                    tag = tag_bytes.decode('utf-8').strip('\x00')  # Remove padding nulls
                except UnicodeDecodeError:
                    tag = f"Invalid Tag Data at Offset {offset}"
                offset += tag_length

                # Now try to read a value associated with the tag
                if offset + 4 <= byte_count:  # Assume a Float (4 bytes)
                    value = snap7.util.get_real(data, offset) #Float value
                    offset += 4
                    points_and_tags[tag] = value
                    print(f"Found Tag: {tag}, Value: {value}")

                elif offset + 2 <= byte_count: #Assume an INT (2 bytes)
                    value = snap7.util.get_int(data, offset)
                    offset += 2
                    points_and_tags[tag] = value
                    print(f"Found Tag: {tag}, Value: {value}")


                else:
                    print(f"Tag: {tag} found, but no associated value could be read.")


            else:
                print("Reached the end of the data block prematurely.")
                break # No more data to read.

        plc.disconnect()
        print("Disconnected from PLC.")
        return points_and_tags

    except snap7.exceptions.Snap7Exception as e:
        print(f"Error communicating with PLC: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    # 1. Attempt to discover the PLC's IP address
    if PLC_IP_ADDRESS is None:
        print("Attempting to discover PLC IP address...")
        PLC_IP_ADDRESS = find_plc_ip_address()
        if PLC_IP_ADDRESS:
            print(f"PLC IP address found: {PLC_IP_ADDRESS}")
        else:
            print("Could not automatically determine PLC IP address.  Please configure manually.")
            exit() #Or prompt for manual input

    # 2. Collect points and tags from the PLC
    if PLC_IP_ADDRESS:
        print("Collecting points and tags...")
        data = collect_points_and_tags(PLC_IP_ADDRESS, PLC_RACK, PLC_SLOT, DB_NUMBER, START_ADDRESS, BYTE_COUNT)

        if data:
            print("\nCollected Points and Tags:")
            for tag, value in data.items():
                print(f"  {tag}: {value}")
        else:
            print("Failed to collect points and tags.")
    else:
        print("PLC IP address not configured.  Exiting.")