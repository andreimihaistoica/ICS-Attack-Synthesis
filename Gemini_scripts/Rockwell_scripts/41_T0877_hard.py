# MITRE ATT&CK Technique T1648: I/O Image
# This script attempts to read the I/O Image from a Rockwell Micro850 PLC.
# It utilizes the Python library pycomm3 to communicate with the PLC.
# Requires:
#   - pycomm3 library installed (pip install pycomm3)
#   - IP address of the PLC
#   - Correct Ethernet/IP path to the PLC

import pycomm3
from pycomm3 import CIPDriver, Services, DataTypes
import socket
import struct

PLC_IP_ADDRESS = "" # Replace with the actual PLC IP address. If empty, script will attempt to find.

# Micro850 doesn't directly expose I/O Image as a tag.
# This script reads the values of specific I/O points
# which represent a partial view of the I/O Image.
# Replace these tags with the I/O points you want to monitor.

IO_TAGS = [
    "_IO_EM_DO_02",  # Fan output
    "_IO_EM_DO_06",  # Red LED
    "_IO_EM_DO_07"   # Green LED
    # "_IO_EM_DI_00", # Example Digital Input
    # Add more I/O points as needed
]

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address on the local network using EtherNet/IP discovery.
    Returns:
        str: The PLC's IP address, or None if not found.
    """
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(5)  # Timeout after 5 seconds

        # Construct the EtherNet/IP discovery message (Generic EIP Service 0x04)
        message = b'\x63\x00'  # Encapsulation Header - Command (List Services Request)
        message += b'\x10\x00'  # Length
        message += b'\x00\x00\x00\x00'  # Session Handle
        message += b'\x00\x00\x00\x00'  # Status
        message += b'\x00\x00\x00\x00'  # Sender Context
        message += b'\x00\x00\x00\x00'  # Options

        # Send the broadcast message
        sock.sendto(message, ('<broadcast>', 44818))

        # Receive the response
        data, addr = sock.recvfrom(1024)
        sock.close()

        # Parse the IP address from the response
        # The IP address is typically found after the "Host Name" string
        try:
            host_name_index = data.find(b'Host Name')
            if host_name_index != -1:
                ip_address_start = host_name_index + len(b'Host Name') + 1  # Move past the "Host Name" string
                ip_address_end = data.find(b'\x00', ip_address_start) # Find the end of the string
                ip_address = data[ip_address_start:ip_address_end].decode('utf-8')

                print(f"Found PLC at IP Address: {ip_address}")
                return ip_address
            else:
                print("Could not parse IP Address from PLC Discovery response.")
                return None
        except Exception as e:
            print(f"Error parsing IP address: {e}")
            return None


    except socket.timeout:
        print("PLC discovery timed out. No PLC found on the network.")
        return None
    except Exception as e:
        print(f"Error during PLC discovery: {e}")
        return None


def read_io_image(ip_address, io_tags):
    """
    Reads the specified I/O tags from the PLC.
    Args:
        ip_address (str): The IP address of the PLC.
        io_tags (list): A list of I/O tag names to read.

    Returns:
        dict: A dictionary containing the tag names and their corresponding values.
              Returns None if there is an error connecting to the PLC.
    """
    try:
        with pycomm3.CIPDriver(ip_address) as plc:  # No explicit path needed for Micro800
            if plc.connected:
                print(f"Connected to PLC at {ip_address}")
                values = plc.read(*io_tags)

                if all(result.status == "Success" for result in values):  # Check if all reads were successful
                    io_image_data = {}
                    for i, result in enumerate(values):
                        io_image_data[io_tags[i]] = result.value
                    return io_image_data
                else:
                    print("Error reading I/O tags:")
                    for i, result in enumerate(values):
                        if result.status != "Success":
                            print(f"  {io_tags[i]}: {result.status}")
                    return None

            else:
                print(f"Failed to connect to PLC at {ip_address}")
                return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":

    if not PLC_IP_ADDRESS:
        PLC_IP_ADDRESS = find_plc_ip()
        if not PLC_IP_ADDRESS:
            print("PLC IP address not provided and could not be discovered.")
            exit()

    io_image = read_io_image(PLC_IP_ADDRESS, IO_TAGS)

    if io_image:
        print("\nI/O Image Data:")
        for tag, value in io_image.items():
            print(f"  {tag}: {value}")
    else:
        print("Failed to retrieve I/O Image data.")