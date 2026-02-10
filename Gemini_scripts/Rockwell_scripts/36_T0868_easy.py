import snap7
import socket
import struct
import time
import subprocess

def find_plc_ip():
    """
    Attempts to find the PLC's IP address by scanning the network.
    This is a basic implementation and might need adjustments 
    depending on your network configuration and PLC model.

    Uses nmap if available, otherwise resorts to a simple ping sweep.
    """
    try:
        # Try using nmap for a more robust discovery
        # Requires nmap to be installed and in the system's PATH
        result = subprocess.run(['nmap', '-sn', '192.168.1.0/24'], capture_output=True, text=True)  # Change to your network range
        output = result.stdout
        
        for line in output.splitlines():
            if "host is up" in line:
                ip_address = line.split()[4] # Get IP address from nmap output
                # Basic validation - improve as needed
                if is_valid_ipv4_address(ip_address):
                  return ip_address
                else:
                  continue
        print("PLC IP not found using nmap. Trying ping sweep...") # Inform the user if nmap fails

    except FileNotFoundError:
        print("Nmap not found.  Falling back to ping sweep.")

    # Simple ping sweep (less reliable but works if nmap is not available)
    # Requires administrator privileges in some environments
    for i in range(1, 255):
        ip_address = "192.168.1." + str(i) # Change to your network range
        try:
            result = subprocess.run(['ping', '-n', '1', '-w', '100', ip_address], capture_output=True, text=True)
            output = result.stdout
            if "TTL=" in output:
                print(f"Found device at {ip_address}")
                return ip_address
        except Exception as e:
            print(f"Error pinging {ip_address}: {e}")
            pass

    print("PLC IP address not found on the network.")
    return None


def is_valid_ipv4_address(address):
    """
    Checks if an address is a valid IPv4 address.
    """
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # inet_pton not available (older Python)
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:
        return False

    return True

def get_plc_operating_mode(plc_ip, rack=0, slot=2):
    """
    Connects to the PLC and attempts to read a specific memory location
    that might indicate the operating mode.  This is highly PLC-specific.

    Args:
        plc_ip (str): IP address of the PLC.
        rack (int): PLC rack number (default: 0).
        slot (int): PLC slot number (default: 2).

    Returns:
        str: Operating mode if successfully detected, otherwise None.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)

        # *** IMPORTANT:  This is where you need to customize the script ***
        # The following section is highly dependent on the PLC model.
        # You need to know the memory address (DB number, byte offset, bit offset)
        # where the operating mode is stored.

        # Example 1: Read a byte from DB10.DBB0 (Data Block 10, Byte 0)
        # This is a placeholder, replace with your actual DB number and offset.
        db_number = 10
        start_byte = 0
        byte_length = 1
        data = plc.db_read(db_number, start_byte, byte_length)

        # Interpret the data to determine the operating mode.  This depends on
        # how the PLC stores the operating mode information.
        #  -  Is it a single byte with specific bits representing the mode?
        #  -  Is it a word with a numerical code for the mode?
        #  -  Is it a string?

        # The following is a placeholder interpretation.  Adjust as needed.
        mode_code = data[0]  # Get the first byte

        if mode_code == 0:
            operating_mode = "Stop"
        elif mode_code == 1:
            operating_mode = "Run"
        elif mode_code == 2:
            operating_mode = "Program"
        elif mode_code == 3:
            operating_mode = "Remote"
        else:
            operating_mode = "Unknown"

        print(f"PLC Operating Mode: {operating_mode}")

        plc.disconnect()
        return operating_mode


    except snap7.exceptions.Snap7Exception as e:
        print(f"Error communicating with PLC: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None



if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        mode = get_plc_operating_mode(plc_ip)
        if mode:
            print(f"Successfully detected PLC operating mode as: {mode}")
        else:
            print("Failed to determine PLC operating mode.")
    else:
        print("Could not find PLC IP address.  Please ensure the PLC is on the network and reachable.")