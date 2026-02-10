import snap7
import struct
import time
import socket

# Configuration
PLC_IP = None  # Initialize PLC_IP to None, will be discovered if necessary.
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER = 1  # Not directly used in this I/O image capture example, but kept for potential future enhancements
START_ADDRESS = 0
SIZE = 1024  # Adjust as needed to capture the full I/O image
OUTPUT_FILE = "io_image_capture.bin"
SCAN_INTERVAL = 1  # Seconds between captures

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address on the local network.
    This is a basic implementation and might need adjustments based on your network setup.
    """
    print("Attempting to discover PLC IP address...")
    # This example uses a broadcast UDP message, which is a common method for PLC discovery.
    # You may need to adapt this based on your specific PLC discovery protocol.

    UDP_IP = "255.255.255.255"  # Broadcast address
    UDP_PORT = 5007 # Siemens discovery port
    MESSAGE = b"S7OnlineDiscovery" # Example discovery message - adapt as necessary

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

    sock.settimeout(5) # Wait for 5 seconds for a response

    try:
        data, addr = sock.recvfrom(1024)
        print("Received discovery response:", data) #added logging
        return addr[0]
    except socket.timeout:
        print("No PLC discovery response received within the timeout. Please ensure discovery is enabled on the PLC and the network allows broadcast messages.")
        return None  # or raise an exception, depending on your error handling strategy
    finally:
        sock.close()

def capture_io_image(plc_ip, rack, slot, start_address, size, output_file):
    """
    Captures the I/O image from the PLC and saves it to a file.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)

        # Read the I/O image (both inputs and outputs combined).  Adapt this based on the PLC's memory layout.
        # This example reads from a starting address of 0 for a specified size.  The actual memory area
        # that constitutes the I/O image will depend on the PLC's configuration.
        # The following gets the inputs and outputs and combines them.
        inputs = plc.read_area(snap7.constants.S7AreaPE, 0, start_address, size) # Area PE: Process Inputs
        outputs = plc.read_area(snap7.constants.S7AreaPA, 0, start_address, size) # Area PA: Process Outputs

        # Concatenate the input and output data. This assumes a simple concatenation is sufficient.
        # Adjust based on your PLC's specific I/O image memory layout.
        io_image = inputs + outputs

        with open(output_file, "wb") as f:
            f.write(io_image)

        print(f"I/O Image captured and saved to {output_file}")

    except Exception as e:
        print(f"Error capturing I/O Image: {e}")
    finally:
        if 'plc' in locals() and plc.get_connected():
            plc.disconnect()

if __name__ == "__main__":
    # Discover PLC IP if not configured
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("PLC IP address could not be discovered.  Please configure it manually.")
            exit()
        else:
            print(f"Discovered PLC IP address: {PLC_IP}")

    try:
        while True:
            capture_io_image(PLC_IP, PLC_RACK, PLC_SLOT, START_ADDRESS, SIZE, OUTPUT_FILE)
            time.sleep(SCAN_INTERVAL)
    except KeyboardInterrupt:
        print("Script interrupted. Exiting.")