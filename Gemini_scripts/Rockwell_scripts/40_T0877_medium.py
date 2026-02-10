import snap7
import socket
import struct

# Configuration
PLC_IP = None  # Initially unknown, will be discovered
PLC_RACK = 0
PLC_SLOT = 1  #Micro850 uses slot 1
DB_NUMBER = 1  # Data Block number to read (change if needed)  adjust based on I/O organization in your PLC
START_ADDRESS = 0  # Starting byte address in the Data Block (change if needed)
READ_SIZE = 20 # Number of bytes to read, determine based on I/O organization. Change as needed. Should be larger for Micro850 than other PLCs.
SCAN_TIME_SECONDS = 5  # Time to wait between scans for I/O image

def find_plc_ip():
    """
    Finds the PLC's IP address by broadcasting on the network and listening for a response.
    This is a simplified version and may need adjustments for specific network configurations.
    """
    global PLC_IP # Allow modification of the global variable
    
    broadcast_address = '<broadcast>'  # Assumes network supports broadcasts
    broadcast_port = 1777  #  Common port, but potentially adjustable
    timeout_seconds = 5

    # Create a UDP socket for broadcasting and receiving
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcasting
    sock.settimeout(timeout_seconds) # Set a timeout to avoid blocking indefinitely
    
    # Construct a simple discovery message.  This should match what the PLC expects.  Adjust as needed.
    discovery_message = b"Discover PLC"

    try:
        sock.bind(('', broadcast_port)) # Bind to any available address
        sock.sendto(discovery_message, (broadcast_address, broadcast_port))  # Send the broadcast

        print(f"Broadcasting discovery message to {broadcast_address}:{broadcast_port}...")
        
        data, addr = sock.recvfrom(1024)  # Listen for a response. Buffer Size is arbitrary.

        PLC_IP = addr[0] # Extract IP address from the received data
        print(f"PLC IP address found: {PLC_IP}")
        return PLC_IP

    except socket.timeout:
        print("No PLC response received within the timeout period.")
        return None
    except Exception as e:
        print(f"An error occurred during IP discovery: {e}")
        return None
    finally:
        sock.close()


def read_io_image(ip_address, rack, slot, db_number, start_address, size):
    """
    Reads the I/O Image from the PLC.

    Args:
        ip_address (str): The IP address of the PLC.
        rack (int): The PLC rack number.
        slot (int): The PLC slot number.
        db_number (int): The Data Block number.
        start_address (int): The starting address in the Data Block.
        size (int): The number of bytes to read.

    Returns:
        bytes: The data read from the I/O image.  Returns None if there's an error.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(ip_address, rack, slot)

        # Read data from the specified Data Block
        data = plc.db_read(db_number, start_address, size)
        plc.disconnect()
        return data

    except snap7.exceptions.Snap7Exception as e:
        print(f"Error reading I/O image: {e}")
        if plc.get_connected():
            plc.disconnect()
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if plc.get_connected():
            plc.disconnect()
        return None



if __name__ == "__main__":
    import time

    # Discover the PLC IP address if not configured
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("Failed to discover PLC IP address.  Exiting.")
            exit()

    print(f"Using PLC IP Address: {PLC_IP}")

    while True:
        io_image_data = read_io_image(PLC_IP, PLC_RACK, PLC_SLOT, DB_NUMBER, START_ADDRESS, READ_SIZE)

        if io_image_data:
            print(f"I/O Image Data (DB{DB_NUMBER}, Address {START_ADDRESS}, Size {READ_SIZE}): {io_image_data.hex()}")
            # You can further process the data here.  For instance, log it to a file:
            # with open("io_image_log.txt", "a") as f:
            #    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: {io_image_data.hex()}\n")
        else:
            print("Failed to read I/O image.")

        time.sleep(SCAN_TIME_SECONDS)