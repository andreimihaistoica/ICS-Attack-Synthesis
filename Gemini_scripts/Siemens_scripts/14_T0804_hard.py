import snap7
import time
import subprocess
import re

# Configuration - Adjust these values as needed
PLC_IP = None  # Will be discovered if None
PLC_RACK = 0
PLC_SLOT = 1
MOTOR_TEMP_ADDRESS = 7  # MW7 is the address for Motor_Temp
REPORTING_TAGS = ["Fan_A", "Fan_B", "Fan_A_Red", "Fan_A_Green", "Fan_B_Red", "Fan_B_Green", "Motor_Status", "Overheating_Check"]  # Tags to block reporting for
REPORTING_TAG_ADDRESSES = {"Fan_A": 0.0, "Fan_B": 0.1, "Fan_A_Red": 0.4, "Fan_A_Green": 0.5, "Fan_B_Red": 0.2, "Fan_B_Green": 0.3, "Motor_Status": 0.7, "Overheating_Check": 0.2}  # Corresponding bit addresses for reporting tags (from tag table)


def find_plc_ip():
    """
    Attempts to discover the PLC IP address using nmap.  Requires nmap to be installed.
    Returns the IP address as a string, or None if not found.
    """
    try:
        # Run nmap to discover Siemens S7 devices
        result = subprocess.run(['nmap', '-p', '102', '-sV', '192.168.1.0/24'], capture_output=True, text=True, check=True)  # Adjust IP range if necessary
        output = result.stdout

        # Regular expression to find the IP address of Siemens S7 PLC
        match = re.search(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output)
        if match:
            ip_address = match.group(1)
            print(f"PLC IP address found: {ip_address}")
            return ip_address
        else:
            print("No Siemens S7 PLC found in the network.")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap: {e}")
        return None
    except FileNotFoundError:
        print("nmap is not installed. Please install nmap to use automatic IP discovery.")
        return None

def connect_to_plc(ip):
    """Connects to the PLC using Snap7."""
    plc = snap7.client.Client()
    plc.set_timeout(timeout=5000)  # Set a timeout for connection attempts

    try:
        plc.connect(ip, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {ip}")
        return plc
    except Exception as e:
        print(f"Error connecting to PLC: {e}")
        return None


def get_motor_temp(plc):
    """Reads the motor temperature from the PLC."""
    try:
        motor_temp = plc.read_area(snap7.client.Areas.MK, 0, MOTOR_TEMP_ADDRESS, 2)  # Read 2 bytes (INT)
        return snap7.util.get_int(motor_temp, 0)  # Convert bytes to integer
    except Exception as e:
        print(f"Error reading motor temperature: {e}")
        return None


def block_reporting_message(plc, tag_name, initial_value=False):
    """Blocks a specific reporting message by setting its value to a fixed value."""
    try:
        # Determine the byte and bit address based on the tag name
        address = REPORTING_TAG_ADDRESSES.get(tag_name)
        if address is None:
            print(f"Error: Tag '{tag_name}' not found in REPORTING_TAG_ADDRESSES.")
            return

        byte_address = int(address)  # Integer part is the byte address
        bit_address = int((address - byte_address) * 10)  # Decimal part indicates the bit within the byte

        # Read the current byte value
        read_data = plc.read_area(snap7.client.Areas.MK, 0, byte_address, 1)

        # Modify the specific bit based on initial_value
        snap7.util.set_bool(read_data, 0, bit_address, initial_value) #Set the bit to always false

        # Write the modified byte back to the PLC
        plc.write_area(snap7.client.Areas.MK, 0, byte_address, read_data)

        print(f"Reporting message for '{tag_name}' blocked.  Forced to {initial_value}")

    except Exception as e:
        print(f"Error blocking reporting message for '{tag_name}': {e}")


def main():
    global PLC_IP
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("PLC IP address not found. Exiting.")
            return

    plc = connect_to_plc(PLC_IP)
    if plc is None:
        return

    try:
        #Initial Block Reporting of all tags:
        print("Blocking initial reporting.")
        for tag in REPORTING_TAGS:
            block_reporting_message(plc, tag, False) #setting all to false.
        
        input("Press Enter to unblock reporting and exit...") #wait for a keyboard input
        
        #Unblock Reportings of all tags
        print("Unblocking all reportings...")
        for tag in REPORTING_TAGS:
            address = REPORTING_TAG_ADDRESSES.get(tag)
            if address is None:
                print(f"Error: Tag '{tag}' not found in REPORTING_TAG_ADDRESSES.")
                continue
            byte_address = int(address)  # Integer part is the byte address
            bit_address = int((address - byte_address) * 10)  # Decimal part indicates the bit within the byte
            read_data = plc.read_area(snap7.client.Areas.MK, 0, byte_address, 1)
            snap7.util.set_bool(read_data, 0, bit_address, False) #Write the original value back (assuming it was initially false)
            plc.write_area(snap7.client.Areas.MK, 0, byte_address, read_data)
            print(f"Reporting message for '{tag}' unblocked.")



    finally:
        if plc.is_connected():
            plc.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    main()