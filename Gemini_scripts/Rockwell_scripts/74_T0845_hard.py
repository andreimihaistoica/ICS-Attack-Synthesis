import snap7
import struct
import socket
import time
import os

# Configuration - adjust these if necessary
PLC_IP = None  # Initially unknown, will be discovered
PLC_RACK = 0
PLC_SLOT = 1  # Micro850 typically uses slot 1
DB_NUMBER = 1  # Data block number containing the program data (adjust if different)
START_ADDRESS = 0  # Starting address to read from the DB
BYTES_TO_READ = 4096 # Example size - increase if needed. You will need to test this
LOCAL_FILE_PATH = "plc_program_dump.bin"  # Where to save the extracted program

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address on the network.
    This is a simplified approach and may not work in all network configurations.
    It relies on broadcasting a simple UDP message and hoping for a response.
    More robust discovery methods might be needed for complex networks,
    potentially involving specific Rockwell discovery protocols.

    Returns:
        str: The IP address of the PLC if found, otherwise None.
    """
    BROADCAST_ADDRESS = '255.255.255.255'
    DISCOVERY_PORT = 2222  # Common Rockwell discovery port

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)  # Timeout after 5 seconds

    message = b"Who is PLC?"  # Adjust this to a known Rockwell discovery message
    try:
        sock.sendto(message, (BROADCAST_ADDRESS, DISCOVERY_PORT))
        print(f"Broadcasted discovery message to {BROADCAST_ADDRESS}:{DISCOVERY_PORT}")
        data, addr = sock.recvfrom(1024) # Buffer size
        print(f"Received discovery response from {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("PLC IP Discovery timed out.  Ensure the PLC is on the network and discovery is enabled.")
        return None
    except Exception as e:
        print(f"Error during PLC IP Discovery: {e}")
        return None
    finally:
        sock.close()


def upload_plc_program(plc_ip, rack, slot, db_number, start_address, bytes_to_read, local_file_path):
    """
    Uploads program data from the PLC to a local file.

    Args:
        plc_ip (str): The IP address of the PLC.
        rack (int): The PLC rack number.
        slot (int): The PLC slot number.
        db_number (int): The data block number to read from.
        start_address (int): The starting address within the DB.
        bytes_to_read (int): The number of bytes to read.
        local_file_path (str): The path to the local file to save the data to.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)
        print(f"Connected to PLC at {plc_ip}, Rack: {rack}, Slot: {slot}")

        # Read data from the PLC's DB
        data = plc.db_read(db_number, start_address, bytes_to_read)
        print(f"Read {len(data)} bytes from DB{db_number}, starting at address {start_address}")


        # Save the data to a local file
        with open(local_file_path, "wb") as f:
            f.write(data)
        print(f"Program data saved to {local_file_path}")

    except snap7.exceptions.Snap7Exception as e:
        print(f"Error communicating with the PLC: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'plc' in locals() and plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    print("Starting PLC Program Upload script...")

    PLC_IP = find_plc_ip()
    if PLC_IP is None:
        print("Could not automatically discover PLC IP address.  Exiting.")
        exit(1)
    print(f"PLC IP address found: {PLC_IP}")


    # Perform the program upload
    upload_plc_program(PLC_IP, PLC_RACK, PLC_SLOT, DB_NUMBER, START_ADDRESS, BYTES_TO_READ, LOCAL_FILE_PATH)

    print("PLC Program Upload script finished.")