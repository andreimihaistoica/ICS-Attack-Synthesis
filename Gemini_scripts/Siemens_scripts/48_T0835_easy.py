import snap7
import socket
import struct

# Configuration - Adjust these values based on your PLC setup
PLC_RACK = 0  # Usually 0 for S7-300/400
PLC_SLOT = 2  # Usually 2 for S7-300/400
TARGET_INPUT_BYTE = 0  # The byte in the input image to manipulate (e.g., I0.0 to I0.7 are in byte 0)
TARGET_INPUT_BIT = 0   # The bit within the byte to manipulate (0-7)
TARGET_OUTPUT_BYTE = 0 # The byte in the output image to manipulate (e.g., Q0.0 to Q0.7 are in byte 0)
TARGET_OUTPUT_BIT = 0  # The bit within the byte to manipulate (0-7)
DESIRED_INPUT_STATE = 1 # 1 to force ON, 0 to force OFF for the input
DESIRED_OUTPUT_STATE = 1 # 1 to force ON, 0 to force OFF for the output
SCAN_TIME_SECONDS = 10 #Duration of the scan cycle

# Function to find the PLC's IP address by broadcasting a discovery message.
def find_plc_ip():
    """
    Broadcasts a discovery message to find the PLC's IP address.

    Returns:
        str: The PLC's IP address, or None if not found.
    """
    broadcast_address = '255.255.255.255'  # Broadcast address
    discovery_port = 1616 #Port for PLC discovery

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #Enable broadcasting
    sock.settimeout(5) #Timeout after 5 seconds
    try:
        sock.bind(('', discovery_port)) # bind to the correct port
    except OSError as e:
        if e.errno == 98: # Address already in use
            print("Error: Port 1616 is already in use. Another program might be using it.  Try closing that program.")
            return None
        else:
            print(f"Error binding to port 1616: {e}")
            return None

    # Craft the discovery message (Simplified, adjust as needed for your PLC)
    discovery_message = b"S7 Discovery"

    try:
        sock.sendto(discovery_message, (broadcast_address, discovery_port))
        print("Discovery message sent. Listening for response...")

        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"PLC IP address found: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("No PLC response received within the timeout period.")
        return None
    except Exception as e:
        print(f"An error occurred during discovery: {e}")
        return None
    finally:
        sock.close()



def manipulate_io_image(plc_ip, rack, slot, input_byte, input_bit, desired_input_state, output_byte, output_bit, desired_output_state):
    """
    Connects to the PLC, manipulates the I/O image, and disconnects.

    Args:
        plc_ip (str): The PLC's IP address.
        rack (int): The PLC's rack number.
        slot (int): The PLC's slot number.
        input_byte (int): The byte of the input image to modify.
        input_bit (int): The bit of the input image to modify (0-7).
        desired_input_state (int): 1 to force ON, 0 to force OFF the input.
        output_byte (int): The byte of the output image to modify.
        output_bit (int): The bit of the output image to modify (0-7).
        desired_output_state (int): 1 to force ON, 0 to force OFF the output.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)
        print(f"Connected to PLC at {plc_ip}, Rack: {rack}, Slot: {slot}")


        # --- Manipulate Input Image ---
        # Read the current input byte
        input_area = snap7.types.Areas.IB  # Input Bytes
        byte_size = 1 #reading 1 byte
        current_input_byte = plc.read_area(input_area, 0, input_byte, byte_size)

        # Modify the specific bit within the byte
        current_value = current_input_byte[0]  # Get the integer value of the byte
        if desired_input_state == 1:
            new_value = current_value | (1 << input_bit)  # Set the bit
        else:
            new_value = current_value & ~(1 << input_bit) # Clear the bit

        # Write the modified byte back to the input image
        new_input_byte = struct.pack('B', new_value) #pack the value into a byte for writing
        plc.write_area(input_area, 0, input_byte, new_input_byte)
        print(f"Input I{input_byte}.{input_bit} forced to {desired_input_state}")


        # --- Manipulate Output Image ---
        # Read the current output byte
        output_area = snap7.types.Areas.QB  # Output Bytes
        current_output_byte = plc.read_area(output_area, 0, output_byte, byte_size)

        # Modify the specific bit within the byte
        current_value = current_output_byte[0]
        if desired_output_state == 1:
            new_value = current_value | (1 << output_bit)  # Set the bit
        else:
            new_value = current_value & ~(1 << output_bit)  # Clear the bit

        # Write the modified byte back to the output image
        new_output_byte = struct.pack('B', new_value)
        plc.write_area(output_area, 0, output_byte, new_output_byte)
        print(f"Output Q{output_byte}.{output_bit} forced to {desired_output_state}")

    except snap7.exceptions.Snap7Exception as e:
        print(f"Error communicating with the PLC: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'plc' in locals() and plc.get_connected():  # Check if plc is defined and connected
            plc.disconnect()
            print("Disconnected from PLC.")

if __name__ == "__main__":
    # 1. Find the PLC IP Address
    plc_ip_address = find_plc_ip()

    if plc_ip_address:
        # 2.  Manipulate the I/O image if the IP was found
        manipulate_io_image(plc_ip_address, PLC_RACK, PLC_SLOT, TARGET_INPUT_BYTE, TARGET_INPUT_BIT, DESIRED_INPUT_STATE, TARGET_OUTPUT_BYTE, TARGET_OUTPUT_BIT, DESIRED_OUTPUT_STATE)
    else:
        print("PLC IP address not found.  Exiting.")