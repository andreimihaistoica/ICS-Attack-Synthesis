# Import necessary libraries
import snap7
import socket
import struct
import time
import os

# Configuration - Defaults, will be overwritten if PLC IP is found
PLC_IP = "0.0.0.0"  # Placeholder - will try to discover
PLC_RACK = 0
PLC_SLOT = 1
LOCAL_TSAP = 0x0300  # Example local TSAP. Ensure this is not in use by other applications.  Find an open port.
REMOTE_TSAP = 0x0200 # Example remote TSAP. Check PLC configuration to find remote TSAP.
DB_NUMBER = 1  # Example Data Block Number. Change as needed.
START_ADDRESS = 0  # Start address in the DB.  Change as needed.
READ_SIZE = 256  # Number of bytes to read. Change as needed.

# --- PLC IP Discovery Function ---
def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address by broadcasting a discovery message.
    This relies on the PLC responding to the discovery.  It may not work with all PLCs/configurations.
    Returns:
        string: PLC IP address if found, otherwise None.
    """
    broadcast_address = '<broadcast>' # Send the discovery message to the broadcast address
    discovery_port = 1616  #Example Discovery port to send the message on

    # Construct the discovery message (a simple text message for demonstration)
    discovery_message = b"PLC_DISCOVERY_REQUEST"  # Example message, adjust as needed

    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(5)  # Timeout after 5 seconds

        # Send the broadcast message
        sock.sendto(discovery_message, (broadcast_address, discovery_port))
        print(f"Broadcasted discovery message to {broadcast_address}:{discovery_port}")

        # Wait for a response
        try:
            data, addr = sock.recvfrom(1024)
            print(f"Received response from {addr}")
            plc_ip = addr[0]
            print(f"PLC IP Address found: {plc_ip}")
            return plc_ip
        except socket.timeout:
            print("No response received from PLC after 5 seconds.")
            return None # Timed out without receiving a response
        finally:
            sock.close()

    except Exception as e:
        print(f"Error during PLC discovery: {e}")
        return None


# ---  Function to read data from PLC ---
def read_plc_data(plc_ip, rack, slot, db_number, start_address, read_size):
    """
    Reads data from a Siemens PLC using snap7.

    Args:
        plc_ip (str):  The IP address of the PLC.
        rack (int): The PLC rack number.
        slot (int): The PLC slot number.
        db_number (int): The Data Block number to read from.
        start_address (int): The starting address within the DB.
        read_size (int): The number of bytes to read.

    Returns:
        bytes: The data read from the PLC, or None on failure.
    """
    try:
        plc = snap7.client.Client()

        # Connect to the PLC using ISO over TCP
        plc.set_iso_connection_params(plc_ip, 102, LOCAL_TSAP, REMOTE_TSAP)  # ISO-on-TCP
        plc.connect(plc_ip, rack, slot)

        # Read data from the Data Block
        data = plc.db_read(db_number, start_address, read_size)
        plc.disconnect()
        print(f"Successfully read {read_size} bytes from DB{db_number} starting at address {start_address}")
        return data

    except Exception as e:
        print(f"Error reading from PLC: {e}")
        return None

# --- Function to log the collected data ---
def log_data(data, filename="plc_data_log.txt"):
    """
    Logs the collected PLC data to a file.

    Args:
        data (bytes): The data to log.
        filename (str): The name of the log file.
    """
    try:
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        log_file_path = os.path.join(os.getcwd(), filename)  # Saves the log file to the current working directory

        with open(log_file_path, "a") as f:  # Append mode to keep a history
            f.write(f"--- Timestamp: {timestamp} ---\n")
            f.write(data.hex() + "\n")  # Log the data in hexadecimal format
        print(f"Data logged to {log_file_path}")

    except Exception as e:
        print(f"Error logging data: {e}")



# --- Main execution block ---
if __name__ == "__main__":

    # 1. Attempt to discover the PLC IP
    discovered_ip = discover_plc_ip()

    if discovered_ip:
        PLC_IP = discovered_ip
        print(f"Using discovered PLC IP: {PLC_IP}")
    else:
        print("PLC IP discovery failed. Using default PLC IP. Ensure that the PLC's IP address is configured correctly to allow successful communication.")
        print(f"Attempting to communicate with PLC IP : {PLC_IP}")

    # 2. Read data from the PLC
    plc_data = read_plc_data(PLC_IP, PLC_RACK, PLC_SLOT, DB_NUMBER, START_ADDRESS, READ_SIZE)

    # 3. Log the data if successfully read
    if plc_data:
        log_data(plc_data)
    else:
        print("Failed to read data from the PLC.")

    print("Script execution completed.")