import snap7
import socket
import struct
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define PLC parameters (defaults - adjust if necessary)
PLC_IP = None  # IP will be found automatically if left as None
RACK = 0
SLOT = 1
DB_NUMBER = 1  # Example Data Block number - CHANGE THIS to the DB containing I/O data
START_ADDRESS = 0  # Start byte address in the DB
DATA_SIZE = 10  # Number of bytes to read from the DB - Adjust according to your I/O size. VERY IMPORTANT.

def find_plc_ip(vendor_name="Schneider Electric"):
    """
    Finds the IP address of a PLC based on vendor name by broadcasting a UDP discovery packet.
    This is a simplified approach and may not work in all network configurations.
    It relies on the PLC responding to a broadcast with its IP.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5) # Timeout after 5 seconds

    # Schneider Electric broadcast message (example - adapt as needed).  This is a PLACEHOLDER.
    # You'll need to research the actual broadcast message for Schneider Electric PLCs to reliably find them.
    message = b"GET_PLC_INFO"  # This is a hypothetical message.  REPLACE WITH THE CORRECT ONE.

    try:
        sock.sendto(message, ('<broadcast>', 30000)) # Use port 30000, a common port.  May need to change.
        logging.info(f"Broadcast message sent to discover {vendor_name} PLC.")
        data, addr = sock.recvfrom(1024)
        logging.info(f"Received response from {addr}")

        # Basic parsing (adapt based on expected response format)
        response_str = data.decode('utf-8', errors='ignore') # Attempt to decode the response.
        if vendor_name in response_str: # Check if vendor name is in response
             return addr[0] # Return the IP address of the sender
        else:
            logging.warning(f"Response received, but vendor name '{vendor_name}' not found.")
            return None

    except socket.timeout:
        logging.warning(f"No response received from any PLC after 5 seconds.")
        return None
    except Exception as e:
        logging.error(f"Error during PLC discovery: {e}")
        return None
    finally:
        sock.close()



def read_io_image(plc_ip, rack, slot, db_number, start_address, data_size):
    """
    Reads the I/O image from a Schneider Electric TM221CE16R PLC using snap7.

    Args:
        plc_ip (str): The IP address of the PLC.
        rack (int): The rack number of the PLC.
        slot (int): The slot number of the PLC.
        db_number (int): The data block number containing the I/O image.
        start_address (int): The starting address within the data block to read from.
        data_size (int): The number of bytes to read.

    Returns:
        bytes: The I/O image data, or None if an error occurred.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)
        logging.info(f"Connected to PLC at {plc_ip}, Rack={rack}, Slot={slot}")

        # Read the data block. Snap7 uses DB area (Area.DB)
        data = plc.db_read(db_number, start_address, data_size)
        logging.info(f"Read {data_size} bytes from DB{db_number}, starting at address {start_address}")

        plc.disconnect()
        logging.info("Disconnected from PLC.")
        return data

    except snap7.exceptions.Snap7Exception as e:
        logging.error(f"Snap7 error: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None


def main():
    global PLC_IP #Use the global PLC_IP variable.

    if PLC_IP is None:
        PLC_IP = find_plc_ip(vendor_name="Schneider Electric")
        if PLC_IP:
            logging.info(f"PLC IP address found: {PLC_IP}")
        else:
            logging.error("Failed to automatically discover PLC IP address.  Please set it manually in the script.")
            return # Stop Execution.

    if not PLC_IP: #Double check
        print("PLC_IP not defined. Please configure the PLC_IP variable.")
        return

    io_image_data = read_io_image(PLC_IP, RACK, SLOT, DB_NUMBER, START_ADDRESS, DATA_SIZE)

    if io_image_data:
        print("I/O Image Data:")
        print(io_image_data)  # Display the raw bytes

        # Example: Convert the data to a human-readable format
        # (Adapt this based on the structure of your I/O data)
        # For example, if the first two bytes represent an integer:
        if DATA_SIZE >= 2:
            value = struct.unpack(">h", io_image_data[0:2])[0]  # Assuming big-endian, 2-byte integer
            print(f"Example value (bytes 0-1): {value}")

        # Further analysis and processing of the data would go here,
        # based on your specific needs.  This could include:
        # - Writing the data to a file
        # - Comparing the data to a baseline
        # - Triggering alerts based on the data

    else:
        print("Failed to read I/O Image Data.")


if __name__ == "__main__":
    main()