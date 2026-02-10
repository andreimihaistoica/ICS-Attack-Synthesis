import pycomm3
import time
import socket
import struct

# Configuration -  Adjust these based on your specific setup
PLC_IP = None  # Will be discovered if not provided
PLC_SLOT = 0  # Default PLC slot for Micro850 is often 0
ALARM_TAG_NAME = 'Alarm1'  # Example: Name of the tag representing the alarm
SUPPRESSION_DURATION = 60  # Suppression duration in seconds
# --- Helper functions ---

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address on the local network.
    This relies on the PLC responding to a UDP broadcast on port 44818.
    """
    # CIP Port
    UDP_PORT = 44818
    # Broadcast Address 
    BROADCAST_ADDRESS = '255.255.255.255'
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)  # Set a timeout for receiving responses

    try:
        # Send a CIP discovery request (minimal)
        discovery_message = b'\x63\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x04\x00' #Minimal discovery message

        sock.sendto(discovery_message, (BROADCAST_ADDRESS, UDP_PORT))

        # Listen for responses
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                #Basic Validation (Check encapsulated protocol version and status)
                if len(data) > 4 and data[0:2] == b'\x63\x00' and data[6:8] == b'\x00\x00':
                    return addr[0]  # Return the IP address of the sender
            except socket.timeout:
                break #No more responses received

    except Exception as e:
        print(f"Error during IP discovery: {e}")
    finally:
        sock.close()

    return None  # PLC not found

def check_alarm_status(plc_ip, plc_slot, alarm_tag):
    """Reads the current status of the alarm tag."""
    try:
        with pycomm3.LogixDriver(plc_ip, slot=plc_slot) as plc:
            status = plc.read(alarm_tag)
            if status.status == 'Success':
                return status.value
            else:
                print(f"Error reading {alarm_tag}: {status.status}")
                return None
    except Exception as e:
        print(f"Error connecting to PLC or reading alarm tag: {e}")
        return None

def suppress_alarm(plc_ip, plc_slot, alarm_tag):
    """Suppresses the alarm by writing '0' (False) to the alarm tag."""
    try:
        with pycomm3.LogixDriver(plc_ip, slot=plc_slot) as plc:
            plc.write(alarm_tag, 0)  # Write 0 (False) to suppress the alarm
            print(f"Alarm '{alarm_tag}' suppressed successfully.")
    except Exception as e:
        print(f"Error suppressing alarm: {e}")


def restore_alarm(plc_ip, plc_slot, alarm_tag, original_value):
    """Restores the alarm to its original value."""
    try:
        with pycomm3.LogixDriver(plc_ip, slot=plc_slot) as plc:
            plc.write(alarm_tag, original_value)  # Restore to original value
            print(f"Alarm '{alarm_tag}' restored to its original value.")
    except Exception as e:
        print(f"Error restoring alarm: {e}")


# --- Main Script ---

if __name__ == "__main__":
    if PLC_IP is None:
        print("Discovering PLC IP address...")
        PLC_IP = find_plc_ip()
        if PLC_IP:
            print(f"PLC IP address found: {PLC_IP}")
        else:
            print("PLC IP address not found.  Please specify it manually in the script.")
            exit()

    print("Starting Alarm Suppression Script...")

    #1. Check initial Alarm status
    initial_alarm_status = check_alarm_status(PLC_IP, PLC_SLOT, ALARM_TAG_NAME)

    if initial_alarm_status is None:
        print("Failed to get initial alarm status. Exiting.")
        exit()

    print(f"Initial alarm status: {initial_alarm_status}")

    # 2. Suppress Alarm
    suppress_alarm(PLC_IP, PLC_SLOT, ALARM_TAG_NAME)

    # 3. Wait for specified duration
    print(f"Alarm suppressed for {SUPPRESSION_DURATION} seconds...")
    time.sleep(SUPPRESSION_DURATION)

    # 4. Restore Alarm
    restore_alarm(PLC_IP, PLC_SLOT, ALARM_TAG_NAME, initial_alarm_status)

    print("Alarm Suppression Script Finished.")