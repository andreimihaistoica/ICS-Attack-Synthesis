import snap7
import socket
import struct

# Configuration - Replace with actual values
PLC_IP = None  # Initially unknown, will be discovered
RACK = 0
SLOT = 1 #Most Micro850s this is 1, but can vary
TARGET_MODE = 'STOP'  # Mode to switch to. Options: 'STOP', 'RUN', ('REMOTE' - not directly settable on many PLCs), others depend on PLC.
#Define function to discover plc ip from device hostname
def resolve_hostname(hostname):
    """Resolves a hostname to an IP address.

    Args:
        hostname: The hostname to resolve (e.g., 'myplc').

    Returns:
        The IP address as a string, or None if the hostname cannot be resolved.
    """
    try:
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.gaierror:
        print(f"Error: Could not resolve hostname '{hostname}'.")
        return None

def find_plc_ip():
    """Attempts to discover the PLC's IP address using various methods.

    This example prioritizes hostname resolution, but you could add other discovery methods like network scanning.  This function needs to be adapted to your specific environment.

    Returns:
        The IP address as a string, or None if the IP address cannot be found.
    """
    # Method 1: Try resolving a known hostname (replace 'myplc' with the actual PLC hostname if known)
    global PLC_IP # Use the global variable
    hostname = 'myplc'  # Replace with your PLC's hostname if you know it.  Leave it empty string if not
    if hostname:
        PLC_IP = resolve_hostname(hostname)
        if PLC_IP:
            print(f"PLC IP address found via hostname resolution: {PLC_IP}")
            return PLC_IP

    # Add other discovery methods here (e.g., network scanning).  A basic, incomplete example:
    # This is very basic and may not work reliably.  Consider using more sophisticated methods.
    #for i in range(1, 255):
    #    potential_ip = f"192.168.1.{i}"  # Adjust the IP range if needed.
    #    try:
    #        # Attempt a simple ping or connection.  This is just an example, and proper network scanning requires more robust techniques.
    #        socket.create_connection((potential_ip, 2000), timeout=0.1)  # Check port 2000 (Rockwell PLC port)
    #        print(f"Possible PLC IP address found: {potential_ip}")
    #        PLC_IP = potential_ip
    #        return PLC_IP # Return the first one found
    #    except (socket.timeout, socket.error):
    #        pass

    print("Warning: Could not automatically discover the PLC's IP address.")
    print("Please set PLC_IP manually in the script.")
    return None

def change_plc_mode(ip_address, rack, slot, target_mode):
    """Changes the operating mode of a Rockwell Micro850 PLC.

    Args:
        ip_address: The IP address of the PLC.
        rack: The rack number.
        slot: The slot number.
        target_mode: The desired operating mode ('STOP', 'RUN').
    """

    try:
        plc = snap7.client.Client()
        plc.connect(ip_address, rack, slot)

        # Micro800 series PLCs typically don't expose a direct API for changing modes like S7-1200/1500.
        # Instead, you often have to manipulate specific memory locations or tags.

        # This example assumes you have a tag or memory location that controls the PLC mode.
        # **Important:** You *must* determine the correct address and data type for your specific PLC program.
        # The following are placeholders - you'll need to adapt them to your actual PLC setup.

        MODE_CONTROL_DB = 10  # Replace with your Data Block number
        MODE_CONTROL_OFFSET = 0  # Replace with the offset within the Data Block
        MODE_CONTROL_DATATYPE = snap7.util.S7WLBit # Replace with the correct data type (Word, Bit, etc.)
        MODE_CONTROL_BYTE = 0
        MODE_CONTROL_BIT = 0 # This is specific if the datatype is bit

        if target_mode.upper() == 'STOP':
            mode_value = 0  # Replace with the value that sets the PLC to Stop mode
            print("Attempting to set PLC to STOP mode...")

        elif target_mode.upper() == 'RUN':
            mode_value = 1 # Replace with the value that sets the PLC to Run mode
            print("Attempting to set PLC to RUN mode...")
        else:
            print(f"Error: Invalid target mode '{target_mode}'.  Supported modes: 'STOP', 'RUN'.")
            plc.disconnect()
            return


        # Write the value to the PLC.  This example writes a bit.
        # Adapt this to match your PLC program's logic.

        #Snap7 has problems writing bit values.  So it is best to write entire byte.
        # First, read the byte
        byte_data = plc.db_read(MODE_CONTROL_DB, MODE_CONTROL_OFFSET, 1) # Read 1 byte
        original_byte_value = byte_data[0]  # Get the byte value

        # Modify the bit
        if mode_value == 1:
            new_byte_value = original_byte_value | (1 << MODE_CONTROL_BIT)  # Set the bit
        else:
            new_byte_value = original_byte_value & ~(1 << MODE_CONTROL_BIT)  # Clear the bit

        # Write the modified byte back to the PLC
        plc.db_write(MODE_CONTROL_DB, MODE_CONTROL_OFFSET, bytes([new_byte_value]))
        print(f"Wrote value {new_byte_value} to DB{MODE_CONTROL_DB}.DBB{MODE_CONTROL_OFFSET} to attempt mode change.")

        plc.disconnect()
        print("Disconnected from PLC.")


    except Exception as e:
        print(f"Error communicating with PLC: {e}")


if __name__ == "__main__":

    # 1. Discover the PLC's IP address.
    PLC_IP = find_plc_ip()

    # 2. If the IP address wasn't discovered, prompt the user to enter it manually.
    if not PLC_IP:
        PLC_IP = input("Enter the PLC's IP address: ")
        if not PLC_IP:
            print("PLC IP address is required.  Exiting.")
            exit()

    # 3.  Change the PLC's mode.
    change_plc_mode(PLC_IP, RACK, SLOT, TARGET_MODE)