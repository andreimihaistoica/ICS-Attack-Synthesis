import snap7
import socket
import time

# MITRE ATT&CK Technique: T1621.001 - Collection: Automated Collection (ICS)
# Sub-technique: Use native control protocols (e.g., OPC, Modbus)

# Configuration
PLC_IP = None # IP address of the PLC (will be discovered)
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER = 1 # Modify this if you are reading from a data block instead of directly from memory.
START_ADDRESS = 0  # Start address of the memory region to read
SIZE = 20  # Number of bytes to read (adjust based on the information you need)

def discover_plc_ip():
    """
    Discovers the PLC's IP address on the network.
    This is a simplified example and may not work in all network configurations.
    A more robust discovery method might involve using network scanning tools or specific industrial protocol discovery mechanisms.
    """
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)  # Set a timeout for receiving a response

        # Broadcast a discovery message (customize this for your PLC's protocol)
        # Schneider PLCs often respond to Modbus/TCP queries
        # This is a very simplistic attempt, tailor it appropriately
        message = b"\x00\x00\x00\x00\x00\x06\x01\x03\x00\x00\x00\x01"  # Modbus read holding register 1
        sock.sendto(message, ('255.255.255.255', 502))  # Broadcast to Modbus port

        # Listen for a response
        data, addr = sock.recvfrom(1024)
        print(f"Received discovery response from {addr[0]}")
        return addr[0]  # Return the IP address of the PLC

    except socket.timeout:
        print("No PLC response received during IP discovery.")
        return None
    except Exception as e:
        print(f"Error during PLC IP discovery: {e}")
        return None
    finally:
        sock.close()


def collect_plc_data(ip_address, rack, slot, db_number, start_address, size):
    """
    Collects data from the PLC using the Snap7 library.

    Args:
        ip_address (str): The IP address of the PLC.
        rack (int): The PLC rack number.
        slot (int): The PLC slot number.
        db_number (int): Data Block number
        start_address (int): The starting address to read from.
        size (int): The number of bytes to read.
    Returns:
        bytes: The data read from the PLC, or None on error.
    """
    try:
        client = snap7.client.Client()
        client.connect(ip_address, rack, slot)
        print(f"Connected to PLC at {ip_address}")

        # Read data from the PLC memory
        #Adjust the ReadArea function to retrieve the data you need (Memory Area, Data Block, etc.)
        #For reading directly from memory (%M, %Q, etc), use S7AreaPE, S7AreaPA, S7AreaMK respectively
        #For reading from a Data Block (DB), use S7AreaDB
        data = client.db_read(db_number,start_address, size)
        #data = client.read_area(snap7.types.S7AreaMK, 0, start_address, size)
        #data = client.read_area(snap7.types.S7AreaPA, 0, start_address, size)

        print(f"Collected {len(data)} bytes from PLC.")

        # Example: Print the raw bytes (can be useful for debugging)
        print(f"Raw data: {data}")

        # Process the data according to the PLC program's memory layout
        # (This is highly dependent on the specific PLC program)
        # For example, to read a BOOL value from M1 (byte 0, bit 1):
        # bool_value = snap7.util.get_bool(data, 0, 1)
        # print(f"M1 value: {bool_value}")
        client.disconnect()
        print("Disconnected from PLC.")
        return data

    except Exception as e:
        print(f"Error collecting data from PLC: {e}")
        if client.get_connected():
            client.disconnect()
        return None


if __name__ == "__main__":

    # Discover the PLC IP address
    PLC_IP = discover_plc_ip()
    if not PLC_IP:
        print("Failed to discover PLC IP address.  Exiting.")
        exit()

    data = collect_plc_data(PLC_IP, PLC_RACK, PLC_SLOT, DB_NUMBER, START_ADDRESS, SIZE)

    if data:
        # Further process and analyze the collected data here
        # For example, you could parse specific variables based on the PLC program structure
        # Store the data to a file for later analysis.
        with open("plc_data.bin", "wb") as f:
            f.write(data)
        print("Data written to plc_data.bin")