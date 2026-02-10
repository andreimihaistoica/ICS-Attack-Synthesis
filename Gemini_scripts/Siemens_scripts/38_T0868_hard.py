import snap7
import struct
import time

# Configuration - Replace with your PLC's actual IP address
PLC_IP = '192.168.0.1'  # Replace with your PLC IP
RACK = 0
SLOT = 1

# Define the memory area and offset for the operating mode switch
#  This will likely need adjusting based on your PLC's configuration
#  and how the operating mode is represented in memory.
#  Consult your PLC documentation for the correct address.
OPERATING_MODE_DB = 1  # Example: Data Block 1
OPERATING_MODE_OFFSET = 0  # Example: Byte offset 0 in the DB
OPERATING_MODE_LENGTH = 1 # Read 1 byte for the mode (adjust as needed)

# Define possible operating mode values (adjust based on your PLC)
# These are just examples.  You'll need to determine the correct values
# from your PLC documentation and the mapping of the switch positions.
MODE_PROGRAM = 0  # Example: 0 represents Program mode
MODE_RUN = 1      # Example: 1 represents Run mode
MODE_REMOTE = 2   # Example: 2 represents Remote mode
MODE_STOP = 3     # Example: 3 represents Stop mode
MODE_RESET = 4    # Example: 4 represents Reset mode
MODE_TEST_MONITOR = 5 # Example: 5 represents Test/Monitor mode

def read_operating_mode(plc):
    """Reads the PLC's operating mode from a specific memory location.

    Args:
        plc: A snap7.client.Client object connected to the PLC.

    Returns:
        The operating mode as an integer, or None if an error occurs.
    """
    try:
        data = plc.db_read(OPERATING_MODE_DB, OPERATING_MODE_OFFSET, OPERATING_MODE_LENGTH)
        # Assuming the mode is stored as a byte. Adjust struct.unpack as needed
        # if it's a word (H), dword (I), etc.
        mode = struct.unpack(">B", data)[0]  # ">B" unpacks as an unsigned byte, big-endian
        return mode
    except Exception as e:
        print(f"Error reading operating mode: {e}")
        return None

def interpret_operating_mode(mode):
    """Interprets the operating mode value and returns a string representation.

    Args:
        mode: The operating mode value (integer).

    Returns:
        A string describing the operating mode, or "Unknown" if the value is not recognized.
    """
    if mode == MODE_PROGRAM:
        return "Program"
    elif mode == MODE_RUN:
        return "Run"
    elif mode == MODE_REMOTE:
        return "Remote"
    elif mode == MODE_STOP:
        return "Stop"
    elif mode == MODE_RESET:
        return "Reset"
    elif mode == MODE_TEST_MONITOR:
        return "Test/Monitor"
    else:
        return "Unknown"

def main():
    """Connects to the PLC and continuously monitors the operating mode."""
    plc = snap7.client.Client()
    plc.set_as_string(True)  # Treat data as strings

    try:
        plc.connect(PLC_IP, RACK, SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        while True:
            mode = read_operating_mode(plc)
            if mode is not None:
                mode_string = interpret_operating_mode(mode)
                print(f"Operating Mode: {mode_string} (Value: {mode})")
            time.sleep(5)  # Check every 5 seconds

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")

if __name__ == "__main__":
    main()