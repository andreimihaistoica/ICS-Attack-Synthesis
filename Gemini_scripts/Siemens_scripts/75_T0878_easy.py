import snap7
import time
import socket
import struct
import subprocess

# Configuration (Adjust these based on your specific setup)
PLC_RACK = 0
PLC_SLOT = 1
ALARM_DB_NUMBER = 10  # Example: The Data Block containing alarm flags
ALARM_BIT_OFFSET = 0.0 # Example: Start at bit 0 of byte 0 in the DB
ALARM_BIT_COUNT = 8  # Example: Assume 8 alarm flags are in the first byte
SUPPRESSION_DURATION = 60 # seconds

# Define alarms (mapping alarm flag index to description)
ALARM_DEFINITIONS = {
    0: "High Temperature Alarm",
    1: "Low Pressure Alarm",
    2: "Tank Level High Alarm",
    3: "Pump Failure Alarm",
    4: "Valve Malfunction Alarm",
    5: "Motor Overload Alarm",
    6: "Communication Error Alarm",
    7: "Process Deviation Alarm"
}

# Function to find PLC IP address via ARP (crude method; refine based on network knowledge)
def find_plc_ip():
    """
    Attempts to find the PLC's IP address by scanning the ARP table.  
    Relies on the engineering workstation (where the script is run) having recently communicated with the PLC.
    This is a *very* basic implementation.  A more robust method would involve SNMP queries, 
    network scanning with nmap (if allowed), or reading a configuration file.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    try:
        # Execute the arp command and capture its output
        arp_output = subprocess.check_output(['arp', '-a']).decode('utf-8')

        # Iterate over the lines in the ARP table output
        for line in arp_output.splitlines():
            parts = line.split()
            if len(parts) >= 4:
                ip_address = parts[1].strip('()')  # Extract the IP address
                mac_address = parts[3]  # Extract the MAC address

                # Check if the MAC address is likely to be a PLC MAC address (manufacturer-specific prefixes)
                # You might need to adjust this based on your PLC's actual MAC address range.
                if mac_address.startswith(('00:0F:EA', '00:0C:29')):  # Example prefixes for Siemens PLCs
                    print(f"Found possible PLC IP address: {ip_address} with MAC: {mac_address}")
                    return ip_address

    except FileNotFoundError:
        print("arp command not found.  Cannot automatically determine PLC IP.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error executing arp command: {e}")
        return None

    print("PLC IP address not found in ARP table.")
    return None


def connect_to_plc(ip_address, rack, slot):
    """Connects to the PLC using Snap7."""
    plc = snap7.client.Client()
    plc.set_timeout(timeout=5000)  # Set a timeout
    try:
        plc.connect(ip_address, rack, slot)
        print(f"Connected to PLC at {ip_address}")
        return plc
    except snap7.exceptions.Snap7Exception as e:
        print(f"Error connecting to PLC at {ip_address}: {e}")
        return None


def read_alarm_status(plc, db_number, bit_offset, bit_count):
    """Reads the current alarm status from the specified DB."""
    try:
        data = plc.db_read(db_number, int(bit_offset), 1) # Read 1 byte from DB
        alarm_byte = data[0]  # Get the first byte
        alarm_statuses = []
        for i in range(bit_count):
            alarm_statuses.append(bool((alarm_byte >> i) & 1)) # Check each bit
        return alarm_statuses
    except Exception as e:
        print(f"Error reading alarm status from DB {db_number}: {e}")
        return None


def suppress_alarms(plc, db_number, bit_offset, bit_count):
    """Suppresses all alarms by writing zeros to the alarm byte in the DB."""
    try:
        data = bytearray([0] * 1)  # Create a byte array with all bits set to 0
        plc.db_write(db_number, int(bit_offset), data)
        print("Alarms suppressed.")
    except Exception as e:
        print(f"Error suppressing alarms in DB {db_number}: {e}")


def restore_alarms(plc, db_number, bit_offset, bit_count, original_alarm_status):
    """Restores the original alarm status by writing the original byte back to the DB."""
    try:
        original_byte = 0
        for i in range(bit_count):
            if original_alarm_status[i]:
                original_byte |= (1 << i)

        data = bytearray([original_byte])  # Create a byte array with the original value
        plc.db_write(db_number, int(bit_offset), data)
        print("Alarms restored.")
    except Exception as e:
        print(f"Error restoring alarms in DB {db_number}: {e}")


def main():
    plc_ip = find_plc_ip()

    if not plc_ip:
        print("Could not automatically determine PLC IP. Please provide it manually.")
        plc_ip = input("Enter PLC IP address: ")

    if not plc_ip:
        print("PLC IP address is required.  Exiting.")
        return

    plc = connect_to_plc(plc_ip, PLC_RACK, PLC_SLOT)
    if not plc:
        return

    # Read initial alarm status
    original_alarm_status = read_alarm_status(plc, ALARM_DB_NUMBER, ALARM_BIT_OFFSET, ALARM_BIT_COUNT)

    if original_alarm_status is None:
        plc.disconnect()
        return

    print("Original Alarm Status:")
    for i, status in enumerate(original_alarm_status):
        print(f"  Alarm {i}: {ALARM_DEFINITIONS.get(i, 'Unknown Alarm')} - {status}")


    # Suppress alarms
    suppress_alarms(plc, ALARM_DB_NUMBER, ALARM_BIT_OFFSET, ALARM_BIT_COUNT)

    # Wait for the specified duration
    time.sleep(SUPPRESSION_DURATION)

    # Restore alarms
    restore_alarms(plc, ALARM_DB_NUMBER, ALARM_BIT_OFFSET, ALARM_BIT_COUNT, original_alarm_status)


    #Disconnect from PLC
    plc.disconnect()
    print("Disconnected from PLC.")


if __name__ == "__main__":
    main()