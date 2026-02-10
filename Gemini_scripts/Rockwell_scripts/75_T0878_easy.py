import snap7
import socket
import struct
import time

# Configuration - Adjust these based on your environment
PLC_RACK = 0
PLC_SLOT = 1
ALARM_BLOCK_DB_NUMBER = 10  # Example DB number containing alarm flags
ALARM_START_BYTE = 0        # Starting byte of alarm flags in the DB
ALARM_BYTE_LENGTH = 4       # Number of bytes containing alarm flags (e.g., 4 bytes = 32 alarm flags)
ALARM_MASK = 0xFFFFFFFF      # Mask to clear all alarm flags in the byte range

# Function to discover the PLC IP address using a basic broadcast ping.
# IMPORTANT: This assumes the PLC is configured to respond to such a ping.
def find_plc_ip():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Broadcast address and port (Adjust if necessary)
    broadcast_address = '255.255.255.255'  # Change if needed
    broadcast_port = 5005  # Example port - Adjust if necessary

    # Message to send (a simple ping request)
    message = b"PLC_PING"  # Example ping message

    # Send the broadcast message
    sock.sendto(message, (broadcast_address, broadcast_port))
    sock.settimeout(5) # Wait for 5 seconds

    try:
        data, addr = sock.recvfrom(1024) # Buffer size
        print(f"Received response from: {addr}")
        plc_ip = addr[0]
        print(f"PLC IP address found: {plc_ip}")
        return plc_ip

    except socket.timeout:
        print("No response received from PLC within timeout.")
        return None
    finally:
        sock.close()


# Function to suppress alarms in the PLC memory (DB)
def suppress_alarms(plc_ip, rack, slot, db_number, start_byte, byte_length, alarm_mask):
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)

        # Read the current alarm byte range
        alarm_data = plc.db_read(db_number, start_byte, byte_length)

        # Convert the byte array to an integer for easier manipulation
        current_alarms = struct.unpack('>I', alarm_data)[0]  # Assuming big-endian integer

        # Suppress alarms by ANDing with the inverse of the mask
        suppressed_alarms = current_alarms & (~alarm_mask)

        # Convert the suppressed alarms back to bytes for writing
        suppressed_data = struct.pack('>I', suppressed_alarms)

        # Write the modified data back to the PLC
        plc.db_write(db_number, start_byte, suppressed_data)
        print(f"Alarms suppressed in DB{db_number}, bytes {start_byte}-{start_byte+byte_length-1} on PLC {plc_ip}")

    except Exception as e:
        print(f"Error suppressing alarms: {e}")
    finally:
        if plc and plc.get_connected():
            plc.disconnect()

# Main Execution Block
if __name__ == "__main__":
    plc_ip_address = find_plc_ip()

    if plc_ip_address:
        print("Running alarm suppression...")
        suppress_alarms(plc_ip_address, PLC_RACK, PLC_SLOT, ALARM_BLOCK_DB_NUMBER,
                        ALARM_START_BYTE, ALARM_BYTE_LENGTH, ALARM_MASK)
        print("Alarm suppression complete.")
    else:
        print("Failed to discover PLC IP address.  Exiting.")