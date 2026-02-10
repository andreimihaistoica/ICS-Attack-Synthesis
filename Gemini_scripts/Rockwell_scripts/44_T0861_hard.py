import pycomm3
import socket

def find_plc_ip():
    """
    Attempts to find the PLC's IP address by broadcasting a discovery request.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(5)  # Timeout after 5 seconds

        # Discovery message (Rockwell's proprietary format)
        discovery_message = b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

        # Broadcast the discovery message
        sock.sendto(discovery_message, ('<broadcast>', 44818))  # Rockwell Discovery Port

        # Listen for a response
        data, addr = sock.recvfrom(1024)
        print(f"Received discovery response from {addr}")
        sock.close()
        return addr[0]  # Return the IP address
    except socket.timeout:
        print("No PLC discovery response received within the timeout period.")
        return None
    except Exception as e:
        print(f"An error occurred during PLC discovery: {e}")
        return None


def collect_plc_tags(plc_ip, tags):
    """
    Collects the values of specified tags from a Rockwell Micro850 PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        tags (list): A list of tag names to collect.

    Returns:
        dict: A dictionary where keys are tag names and values are their corresponding values
              as read from the PLC.  Returns None if there's a connection error.
    """
    try:
        with pycomm3.CIPDriver(plc_ip) as driver:
            print(f"Successfully connected to PLC at {plc_ip}")

            results = driver.read(*tags)  # Read multiple tags in one go
            tag_values = {}
            for tag, result in zip(tags, results):
                if result.status == 'Success':
                    tag_values[tag] = result.value
                    print(f"Tag: {tag}, Value: {result.value}")
                else:
                    print(f"Error reading tag {tag}: {result.status}")
                    tag_values[tag] = None # Mark that tag couldn't be read

            return tag_values

    except Exception as e:
        print(f"Error communicating with PLC: {e}")
        return None


if __name__ == "__main__":
    # Attempt to discover the PLC's IP address
    plc_ip = find_plc_ip()

    if not plc_ip:
        print("PLC IP address not found.  Please manually enter the PLC IP address.")
        plc_ip = input("Enter the PLC IP address: ")
        if not plc_ip:
            print("No PLC IP address provided. Exiting.")
            exit()


    # Define the list of tags to collect
    tags_to_collect = [
        "NewVariable",
        "Activate_FanA",
        "FanA_Timer",
        "START",
        "STOP",
        "TON_1.Q",
        "TONOFF_1.Q",
        "FanA_Off",
        "Tog_Off",
        "_IO_EM_DO_02", # Adding Output
        "_IO_EM_DO_06", # Adding Output
        "_IO_EM_DO_07"  # Adding Output
    ]

    # Collect the tag values
    tag_values = collect_plc_tags(plc_ip, tags_to_collect)

    if tag_values:
        print("\nCollected Tag Values:")
        for tag, value in tag_values.items():
            print(f"{tag}: {value}")
    else:
        print("Failed to collect tag values.")