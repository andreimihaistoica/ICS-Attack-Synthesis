import snap7
import socket
import struct
import time

# Configuration - Modify as needed
PLC_IP = None  # Initially unknown, to be discovered
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER = 1  # Adjust if PLC operating mode is stored in a specific DB
DB_START = 0    # Adjust if offset is needed within DB
DB_LENGTH = 1    # Assuming the operating mode is a single byte

# Define possible PLC operating modes (adjust based on your PLC's documentation)
OPERATING_MODES = {
    0: "STOP",  # Or whatever value represents STOP on your PLC
    1: "RUN",   # Or whatever value represents RUN on your PLC
    2: "REMOTE", # Or whatever value represents REMOTE on your PLC
    3: "PROGRAM", # Or whatever value represents PROGRAM on your PLC
    4: "TEST/MONITOR",  # Or whatever value represents TEST/MONITOR on your PLC
    5: "RESET", # Or whatever value represents RESET on your PLC
    # Add other modes and their corresponding values as needed.
}

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address on the network.
    This is a basic implementation and may not work in all network configurations.
    Consider using more robust discovery methods if this fails.  A proper discovery 
    would be to issue a broadcast ping or other network protocol specific to your PLC.
    """
    # This is a simplified example.  You MUST adapt it to your network.
    # In a real environment, you'd likely query a network management system or
    # use a more sophisticated discovery protocol.
    # The following code simulates a successful IP address discovery, replace with your network scan/query tool.
    print("Attempting to discover PLC IP address...")
    # Replace with your actual discovery logic here
    # In a real-world scenario, you'd scan your network for the PLC's MAC address or hostname.
    # For this simulation, we assume the address is discoverable and fixed.
    
    #Simulated results:
    return "192.168.1.10"

    #return None  # If discovery fails

def read_operating_mode(plc_ip, rack, slot, db_number, db_start, db_length):
    """Reads the PLC's operating mode from a specified DB."""
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)

        # Read the operating mode from the specified DB.
        data = plc.db_read(db_number, db_start, db_length)
        plc.disconnect()  # Disconnect after reading

        # Convert the data to an integer (assuming it's a single byte).
        operating_mode_value = struct.unpack(">B", data)[0]  # ">B" for unsigned byte, big-endian

        return operating_mode_value

    except Exception as e:
        print(f"Error reading operating mode: {e}")
        return None

def interpret_operating_mode(mode_value):
    """Interprets the numerical operating mode value."""
    if mode_value in OPERATING_MODES:
        return OPERATING_MODES[mode_value]
    else:
        return f"Unknown Operating Mode Value: {mode_value}"


def main():
    global PLC_IP  # Use the global variable

    # IP address discovery
    PLC_IP = find_plc_ip()
    if PLC_IP is None:
        print("Failed to discover PLC IP address.  Please configure manually.")
        return  # Exit if IP discovery fails
    else:
        print(f"Discovered PLC IP address: {PLC_IP}")

    try:
        while True:
            # Read the operating mode from the PLC.
            operating_mode_value = read_operating_mode(PLC_IP, PLC_RACK, PLC_SLOT, DB_NUMBER, DB_START, DB_LENGTH)

            if operating_mode_value is not None:
                # Interpret the operating mode.
                operating_mode = interpret_operating_mode(operating_mode_value)
                print(f"PLC Operating Mode: {operating_mode}")
            else:
                print("Failed to read operating mode.")

            time.sleep(5)  # Check every 5 seconds (adjust as needed)

    except KeyboardInterrupt:
        print("Script interrupted.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()