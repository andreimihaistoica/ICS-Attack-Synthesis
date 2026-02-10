import snap7
import time
import socket
import struct
import subprocess

# Configuration - ADJUST THESE BASED ON YOUR ENVIRONMENT
PLC_IP = None  # Will be auto-detected if left as None
PLC_RACK = 0
PLC_SLOT = 1
ALARM_DB_NUMBER = 10  # Example: Database number holding alarm bits/data
ALARM_BIT_OFFSET = 0 # Byte offset within the DB where the alarm bit starts. Adjust if necessary
ALARM_BIT_NUMBER = 0 # Bit number (0-7) within the byte at ALARM_BIT_OFFSET. Adjust if necessary

SUPPRESSION_DURATION = 60  # Duration in seconds to suppress the alarm

# --- Function to Find PLC IP Address ---
def find_plc_ip():
    """
    Attempts to find the PLC's IP address by scanning the network.  This requires nmap
    to be installed and accessible in the system's PATH.
    """
    try:
        # Adjust the IP range if needed for your specific network.  This scans the 192.168.1.0/24 network.
        nmap_command = ["nmap", "-sn", "192.168.1.0/24"]
        process = subprocess.Popen(nmap_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if stderr:
            print(f"Error during network scan: {stderr.decode()}")
            return None

        output = stdout.decode()
        for line in output.splitlines():
            if "Siemens" in line or "SIMATIC" in line:  # Look for a Siemens device.  This might need adjustment.
                parts = line.split()
                ip_address = parts[-1].strip("()")  # Extract IP address from the nmap output.
                print(f"Found PLC IP address: {ip_address}")
                return ip_address

        print("PLC IP address not found. Ensure nmap is installed and accessible, and the IP range is correct.")
        return None

    except FileNotFoundError:
        print("nmap not found. Please install nmap and ensure it's in your system's PATH.")
        return None
    except Exception as e:
        print(f"An error occurred during IP address discovery: {e}")
        return None

# --- Function to Suppress the Alarm ---
def suppress_alarm(plc_ip, db_number, bit_offset, bit_number, duration):
    """
    Suppresses an alarm by clearing the specified bit in the PLC's DB.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {plc_ip}")

        # Read the byte containing the alarm bit
        byte_data = plc.db_read(db_number, bit_offset, 1) # Read 1 byte

        # Clear the specific bit
        original_byte = byte_data[0]  # Get the byte value
        mask = 1 << bit_number # Create a mask to isolate the alarm bit
        modified_byte = original_byte & ~mask # Clear the bit using bitwise AND and NOT

        # Write the modified byte back to the PLC
        write_data = bytearray([modified_byte])
        plc.db_write(db_number, bit_offset, write_data)

        print(f"Alarm bit {bit_number} in DB {db_number}, byte offset {bit_offset} suppressed for {duration} seconds.")

        time.sleep(duration)  # Suppress for the specified duration

        # Restore the alarm bit (set it back to its original value.  This is simplistic and may not be appropriate in all situations.  Ideally you'd read the original state and restore *that*, but this is harder to implement safely.)
        # Read the byte again *after* the wait, in case something else has changed it.  Important for safety.
        byte_data = plc.db_read(db_number, bit_offset, 1)
        original_byte = byte_data[0]

        mask = 1 << bit_number # re-create the mask
        modified_byte = original_byte | mask  # SET the alarm bit.

        write_data = bytearray([modified_byte])
        plc.db_write(db_number, bit_offset, write_data)
        print(f"Alarm bit {bit_number} in DB {db_number}, byte offset {bit_offset} restored.")


    except snap7.exceptions.Snap7Exception as e:
        print(f"Error communicating with the PLC: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'plc' in locals() and plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")


# --- Main Execution ---
if __name__ == "__main__":
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("Could not determine PLC IP address.  Please set PLC_IP manually.")
            exit(1)

    suppress_alarm(PLC_IP, ALARM_DB_NUMBER, ALARM_BIT_OFFSET, ALARM_BIT_NUMBER, SUPPRESSION_DURATION)