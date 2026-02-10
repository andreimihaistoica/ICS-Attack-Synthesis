import snap7
import snap7.util
import socket
import struct
import time
import os

# Configuration - ADJUST THESE VALUES
DB_NUMBER = 1  # Adjust based on your PLC configuration
START_ADDRESS = 0  # Start reading from this byte in the DB
READ_LENGTH = 256 # Adjust based on your needs.  Read more bytes than you need, and filter later if necessary.
TIMEOUT_SECONDS = 5 # Timeout for socket operations.  Increase if you have slow network.

# Function to discover PLC IP Address (very basic UDP broadcast method)
def discover_plc_ip():
    """
    Discovers the PLC's IP address by sending a broadcast UDP message and listening for a response.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    BROADCAST_PORT = 5007 #Siemens PLCs often use port 5007 for discovery.  This may need adjustment.
    BROADCAST_ADDRESS = '255.255.255.255' # Broadcast address. This may need adjustment based on network configuration
    DISCOVERY_MESSAGE = b"GET_PLC_IP"  # Simple message.  Adjust if needed based on PLC discovery protocol.

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcasting
        sock.settimeout(TIMEOUT_SECONDS) # set timeout
        sock.bind(('', 0))  # Bind to a random port

        sock.sendto(DISCOVERY_MESSAGE, (BROADCAST_ADDRESS, BROADCAST_PORT))
        print(f"Sent broadcast message to {BROADCAST_ADDRESS}:{BROADCAST_PORT}")

        try:
            data, addr = sock.recvfrom(1024) #listen for reply, max 1024 byte buffer.
            plc_ip = addr[0] #first element from tuple returned by recvfrom is IP address
            print(f"Received response from PLC: {plc_ip}")
            return plc_ip
        except socket.timeout:
            print("No response from PLC after timeout.")
            return None

    except socket.error as e:
        print(f"Socket error during discovery: {e}")
        return None
    finally:
        sock.close()


def read_plc_data(plc_ip, db_number, start_address, read_length):
    """
    Reads data from the specified DB in the PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        db_number (int): The DB number to read from.
        start_address (int): The starting address in the DB.
        read_length (int): The number of bytes to read.

    Returns:
        bytes: The data read from the PLC, or None if an error occurred.
    """
    try:
        plc = snap7.client.Client()
        plc.set_timeout(TIMEOUT_SECONDS * 1000)  # Set timeout in milliseconds (convert seconds to milliseconds)

        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 (typical for S7-1200)
        print(f"Connected to PLC at {plc_ip}")


        data = plc.db_read(db_number, start_address, read_length)
        plc.disconnect()
        print("Disconnected from PLC.")
        return data

    except snap7.exceptions.Snap7Exception as e:
        print(f"Snap7 error: {e}")
        if plc and plc.get_connected():
          plc.disconnect() #attempt a disconnect if possible after an exception
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if plc and plc.get_connected():
          plc.disconnect() #attempt a disconnect if possible after an exception
        return None


def extract_tags_and_values(data, db_number, start_address):
    """
    Extracts potential tag names and their corresponding values from the raw data.

    This is a rudimentary approach and might require significant refinement based on
    how tags are actually stored in the DB.  This assumes null-terminated strings for tags,
    and attempts to interpret subsequent bytes as numerical values.

    Args:
        data (bytes): The raw data read from the PLC.
        db_number (int): The DB number.
        start_address (int): The starting address.

    Returns:
        list: A list of dictionaries, where each dictionary contains a tag name and its value.
    """
    results = []
    i = 0
    while i < len(data):
        # Attempt to extract a tag (null-terminated string)
        try:
            tag = data[i:].split(b'\x00', 1)[0].decode('ascii', errors='ignore').strip()  # Read until null, decode, and strip whitespace

            if tag: # Only process if the tag is not empty

                i += len(tag) + 1 # Move pointer past the tag and null terminator.

                # Attempt to interpret the following bytes as a numeric value.  This is where you'll need
                # to adjust based on your PLC data types (INT, REAL, etc.).  This example assumes REAL (float).
                if i + 4 <= len(data):  # Check if there are enough bytes for a REAL (4 bytes)
                    value = struct.unpack('>f', data[i:i+4])[0]  #Unpack a big-endian float
                    i += 4
                    results.append({'db': db_number, 'address': start_address + (i - len(tag) - 5), 'tag': tag, 'value': value})
                else:
                    #Not enough bytes to extract a REAL, skip to the next potential tag.
                    print(f"Warning: Insufficient bytes to extract REAL value after tag '{tag}' at address {start_address + i}.")
                    i = len(data) # force exit of loop.

            else:
                i += 1 # No tag found, move to the next byte

        except Exception as e:
            print(f"Error extracting tag: {e}")
            i += 1  # Move to the next byte in case of errors

    return results

def save_results_to_file(results, filename="plc_data.txt"):
    """
    Saves the extracted tag and value data to a file.

    Args:
        results (list):  A list of dictionaries, where each dictionary contains a tag name and its value.
        filename (str): The name of the file to save the data to.
    """
    try:
        with open(filename, "w") as f:
            f.write("PLC Data Extraction Results:\n")
            f.write("-----------------------------\n")
            for item in results:
                f.write(f"DB:{item['db']}, Address: {item['address']}, Tag: {item['tag']}, Value: {item['value']}\n")
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving data to file: {e}")

def main():
    """
    Main function to orchestrate the PLC data extraction.
    """

    plc_ip = discover_plc_ip()

    if not plc_ip:
        print("PLC IP address not found.  Please ensure the PLC is on the network and the discovery port is correct.")
        return

    raw_data = read_plc_data(plc_ip, DB_NUMBER, START_ADDRESS, READ_LENGTH)

    if raw_data:
        extracted_data = extract_tags_and_values(raw_data, DB_NUMBER, START_ADDRESS)
        if extracted_data:
            print("Extracted data:")
            for item in extracted_data:
                print(f"DB:{item['db']}, Address: {item['address']}, Tag: {item['tag']}, Value: {item['value']}")
            save_results_to_file(extracted_data)
        else:
            print("No tags or values were extracted.")
    else:
        print("Failed to read data from the PLC.")


if __name__ == "__main__":
    main()