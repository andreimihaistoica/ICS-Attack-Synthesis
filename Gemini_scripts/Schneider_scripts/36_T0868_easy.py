# MITRE ATT&CK Technique T0820: Detect Operating Mode
# This script attempts to identify the PLC's operating mode by reading specific diagnostic registers.
# This script utilizes the pycomm3 library to communicate with Allen-Bradley PLCs over Ethernet/IP.
# Adapt to your specific PLC vendor/protocol if necessary.

import time
import socket
from pycomm3 import CIPDriver, LogixDriver, exceptions

# Configuration
# PLC_IP = "192.168.1.10"  # Replace with the PLC's IP address.  Commented out because we find it dynamically.
PLC_PORT = 44818  # Standard EtherNet/IP port
TIMEOUT = 5  # Timeout for socket connections and PLC communication in seconds

# Diagnostic Tags (Adapt to your PLC model and memory map)
OPERATING_MODE_TAG = "OperatingMode"  #Example Tag, will need to be changed for your particular PLC
#STATUS_WORD_TAG = "StatusWord"  # Example Tag, will need to be changed for your particular PLC
#CONTROL_WORD_TAG = "ControlWord" # Example Tag, will need to be changed for your particular PLC

def find_plc_ip():
    """
    Finds the PLC's IP address on the network.
    This function performs a simple UDP broadcast to discover devices.
    Note: This requires the PLC to respond to broadcast discovery requests, which is not always the case and may require configuration on the PLC side.
    """

    UDP_IP = "255.255.255.255"  # Broadcast address
    UDP_PORT = 44818  # Standard EtherNet/IP port
    MESSAGE = b"\x63\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00"  # Simple EtherNet/IP discovery message

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)  # Set a timeout for receiving a response
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcasting

    try:
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        print("Broadcast discovery message sent. Waiting for response...")

        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes

        print(f"Received response from {addr[0]}")
        return addr[0]  # Return the IP address of the sender
    except socket.timeout:
        print("No response received from PLC within timeout.")
        return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None
    finally:
        sock.close()


def get_plc_operating_mode(plc_ip):
    """
    Attempts to read the PLC's operating mode by reading predefined tags.

    Args:
        plc_ip (str): The IP address of the PLC.

    Returns:
        str: The PLC's operating mode if successfully read, otherwise None.
    """

    try:
        with LogixDriver(plc_ip) as plc:
            plc.timeout = TIMEOUT
            # Read the operating mode tag.  If you have status word, you'll need to decode the status word
            # to find the operating mode bits. The following logic would need to be customized.
            try:
                op_mode_read = plc.read(OPERATING_MODE_TAG)
                if op_mode_read.status == 'Success':
                    operating_mode = op_mode_read.value
                    print(f"PLC Operating Mode Tag Value: {operating_mode}")

                    #Interpret the operating mode based on the Tag Value
                    if operating_mode == 0: # Example Interpretation, change for your PLC
                        op_mode_string = "Program Mode (Assumed, Tag Value=0)"
                    elif operating_mode == 1:
                        op_mode_string = "Run Mode (Assumed, Tag Value=1)"
                    elif operating_mode == 2:
                        op_mode_string = "Remote Mode (Assumed, Tag Value=2)"
                    elif operating_mode == 3:
                        op_mode_string = "Stop Mode (Assumed, Tag Value=3)"
                    else:
                        op_mode_string = "Unknown Mode (Assumed, Tag Value != 0, 1, 2 or 3)"
                    return op_mode_string

                else:
                    print(f"Error reading {OPERATING_MODE_TAG}: {op_mode_read.status}")
                    return None

            except exceptions.CommError as e:
                print(f"Communication error reading operating mode tag: {e}")
                return None
            except Exception as e:
                print(f"Unexpected error reading operating mode tag: {e}")
                return None

    except exceptions.CommError as e:
        print(f"Failed to connect to PLC at {plc_ip}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None




if __name__ == "__main__":
    print("Starting PLC Operating Mode Detection...")

    plc_ip_address = find_plc_ip()  # Attempt to discover the PLC IP

    if plc_ip_address:
        print(f"PLC IP Address found: {plc_ip_address}")
    else:
        print("PLC IP Address not found.  Exiting.")
        exit()


    #plc_ip_address = input("Enter the PLC's IP address: ") # If auto-discovery fails, you can prompt.

    if plc_ip_address:
        operating_mode = get_plc_operating_mode(plc_ip_address)

        if operating_mode:
            print(f"The PLC is in {operating_mode}")
        else:
            print("Could not determine the PLC's operating mode.")
    else:
        print("No PLC IP address provided.  Exiting.")

    print("PLC Operating Mode Detection complete.")