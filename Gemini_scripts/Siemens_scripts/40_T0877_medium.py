import snap7
import struct
import socket
import time

# Configuration
PLC_IP = None  # Initially set to None, will be discovered if needed
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER = 1  # Example: Adjust if you want to read data from a DB
START_ADDRESS = 0  # Example: Start byte address in the DB
SIZE_BYTES = 10   # Example: Number of bytes to read from the DB

def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the network.
    This is a simplified example and might require adjustments based on network configuration.
    """
    print("Attempting to discover PLC IP address...")
    # Create a socket to listen for broadcast messages
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", 30718))  # Siemens uses port 30718 for discovery (often, but not always)
    sock.settimeout(5)  # Timeout after 5 seconds

    try:
        # Send a broadcast message to trigger PLC responses.  Needs to be tailored for your Siemens PLC and network.
        # A simple broadcast doesn't always work. You may need to format a specific request.
        # The example below is very basic and may not trigger a response.
        broadcast_message = b"s7online"
        sock.sendto(broadcast_message, ('<broadcast>', 30718)) # '<broadcast>' is system dependent. May need '255.255.255.255'

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                print(f"Received message: {data.decode()} from {addr}")  # Decode and print the received data
                # Add logic here to parse the received data and extract the PLC IP address.
                # Siemens discovery protocols are complex and depend on the PLC configuration.
                # The example below is a VERY rudimentary check.  Adapt it based on the PLC response.
                if "Siemens" in data.decode(): #Basic Check if the Word 'Siemens' is in the message.
                  return addr[0] #Return IP Address.

            except socket.timeout:
                print("No PLC IP address discovered after timeout.")
                return None

    finally:
        sock.close()



def read_io_image(ip_address, rack, slot, db_number, start_address, size_bytes):
    """
    Reads the I/O image (or a portion of a Data Block) from the PLC.

    Args:
        ip_address (str): The IP address of the Siemens S7-1200 PLC.
        rack (int): The PLC rack number.
        slot (int): The PLC slot number.
        db_number (int): The Data Block number to read (use 0 for I/O direct access).
        start_address (int): The starting byte address in the DB.
        size_bytes (int): The number of bytes to read.

    Returns:
        bytes: The data read from the PLC, or None on error.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(ip_address, rack, slot)

        if db_number == 0:  # Directly access I/O  (Use this instead of the DB Example)
            # Reading Input Memory (I)
            input_data = plc.read_area(snap7.client.Areas.PAI, 0, start_address, size_bytes)  # PAI = Process Input Image
            print(f"Input Memory (I) Data: {input_data}")
            # Reading Output Memory (Q)
            output_data = plc.read_area(snap7.client.Areas.PAO, 0, start_address, size_bytes) # PAO = Process Output Image
            print(f"Output Memory (Q) Data: {output_data}")

            plc.disconnect()

            #Return both, so the Main routine can pick what it needs.
            return input_data, output_data #return both input and output data
        else:
            # Example: Read from a Data Block (DB)
            db_data = plc.db_read(db_number, start_address, size_bytes)
            print(f"Data Block {db_number} Data: {db_data}")

            plc.disconnect()
            return db_data, None #Return DB Data and None for the Output data.

    except Exception as e:
        print(f"Error reading I/O image: {e}")
        if plc and plc.get_connected(): # Ensure that PLC will Disconnect if it has been created and connected.
            plc.disconnect()
        return None, None


if __name__ == "__main__":

    # 1. Discover PLC IP (if not already known)
    if PLC_IP is None:
        PLC_IP = discover_plc_ip()
        if PLC_IP is None:
            print("Failed to discover PLC IP.  Please provide it manually.")
            exit()
        else:
            print(f"Discovered PLC IP: {PLC_IP}")

    # 2. Read the I/O Image
    input_data, output_data = read_io_image(PLC_IP, PLC_RACK, PLC_SLOT, DB_NUMBER, START_ADDRESS, SIZE_BYTES)

    if input_data: # Check if the data is from Input Memory.
      print("Successfully read input Image")
    elif output_data: # Check if the Data is from the Output Memory.
      print("Successfully read output Image")
    else:
      print("Successfully read DataBlock")

    # Example: Process the collected data (replace with your actual logic)
    # This is just a demonstration.  You'll likely need to parse the byte data
    # according to your PLC's data structure.
    # if data:
    #     print("Collected I/O Image Data:")
    #     print(data)  # Prints the raw bytes

    #     #Example of writing the captured data to a file:
    #     with open("io_image.bin", "wb") as f:
    #         f.write(data)
    #     print("I/O Image data saved to io_image.bin")

    #     # Further processing (example: unpacking specific values) - VERY EXAMPLE SPECIFIC
    #     # Adapt based on YOUR PLC's data layout.
    #     # if len(data) >= 4:
    #     #     value = struct.unpack('>f', data[0:4])[0] # Example: Unpack a float
    #     #     print(f"Extracted float value: {value}")