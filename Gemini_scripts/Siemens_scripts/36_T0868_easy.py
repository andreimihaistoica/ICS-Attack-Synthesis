import snap7
import socket
import struct
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration -  Modify these according to your setup
# You may need to adjust rack and slot depending on your PLC model
PLC_RACK = 0
PLC_SLOT = 1
PLC_DEFAULT_PORT = 102 # S7 default port

def find_plc_ip():
    """
    Attempts to discover the PLC IP address via a simple broadcast ping.
    This is a very basic method and might not work in all network environments.
    More robust discovery methods exist (e.g., using industrial protocols) but are beyond the scope
    of this simplified example.  Requires the engineering workstation to be configured to broadcast.
    """
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)  # Timeout after 2 seconds

        # Craft a simple discovery message (can be anything, really)
        message = b"PLC_DISCOVERY_REQUEST"

        # Broadcast to the local network (255.255.255.255)
        sock.sendto(message, ('255.255.255.255', PLC_DEFAULT_PORT))
        logging.info("Sent PLC discovery request...")

        # Listen for a response
        try:
            data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            logging.info(f"Received response from: {addr[0]}")
            sock.close()
            return addr[0] # Return the IP address

        except socket.timeout:
            logging.warning("No PLC response received within the timeout period.")
            sock.close()
            return None

    except Exception as e:
        logging.error(f"Error during PLC discovery: {e}")
        return None



def get_plc_mode(plc_ip):
    """
    Reads a specific memory location on the PLC that is assumed to hold the operating mode.
    **Important:** This is a simplified example and heavily relies on knowing the PLC's internal memory structure.
    The address (DB number, byte offset, bit offset)  where the operating mode is stored is highly specific to
    the PLC model and the way the PLC program is written.  You **must** determine the correct address
    for your specific PLC.  Consult the PLC's documentation and the program code running on the PLC.

    This example reads from DB10, byte 0, bit 0. This is just an example.  Adjust accordingly.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)
        logging.info(f"Connected to PLC at {plc_ip}")

        # Example: Read a single bit from DB10, Byte 0, Bit 0.
        # This is a placeholder - replace with the actual address of the operating mode in your PLC.
        db_number = 10
        start_byte = 0
        bit_offset = 0
        data = plc.db_read(db_number, start_byte, 1)  # Read 1 byte
        plc.disconnect()
        logging.info("Disconnected from PLC.")

        # Extract the bit value.
        mode_bit = (data[0] >> bit_offset) & 1  #Right shift data[0] by bit_offset positions and the & 1 to extract just the one's value
        logging.info(f"Raw data read from PLC: {data.hex()}")
        return mode_bit

    except Exception as e:
        logging.error(f"Error reading PLC mode: {e}")
        return None



def interpret_mode(mode_bit):
    """
    Interprets the read bit as a PLC mode.  This is a very basic interpretation.
    In a real-world scenario, the operating mode might be represented by multiple bits or bytes,
    requiring a more complex interpretation.

    This example assumes:
    - 0: Run mode
    - 1: Program mode
    Adjust this logic based on your PLC's specific representation of operating modes.
    """
    if mode_bit is None:
        return "Unknown"
    elif mode_bit == 0:
        return "Run"
    elif mode_bit == 1:
        return "Program"
    else:
        return "Indeterminate"  # Add a fallback for unexpected values



def main():
    """
    Main function to discover the PLC, read its operating mode, and print the result.
    """
    plc_ip = find_plc_ip()

    if plc_ip:
        logging.info(f"PLC IP Address: {plc_ip}")
        mode_bit = get_plc_mode(plc_ip)

        if mode_bit is not None:
            mode = interpret_mode(mode_bit)
            print(f"PLC Operating Mode: {mode}")
            logging.info(f"PLC Operating Mode: {mode}")
        else:
            print("Failed to read PLC operating mode.")
    else:
        print("Could not find PLC IP address.")
        logging.warning("PLC IP Address not found, check network configurations.")

if __name__ == "__main__":
    main()