import snap7
import socket
import struct
import time

# Configuration - ADJUST THESE VALUES
PLC_IP = None  # Initially unknown, will be discovered
RACK = 0
SLOT = 1
NEW_PASSWORD = "MyNewSecurePassword123"  # Replace with a strong password
PASSWORD_ADDRESS = 0  # Memory address where the password is stored in the PLC (likely a DB)
PASSWORD_DATA_BLOCK = 100 # Data block where password resides. Adjust based on PLC configuration
PASSWORD_LENGTH = 32 # Assumes password is a string encoded as bytes, padded to a certain length
# Password length may vary depending on your PLC project. Ensure that this matches the length in the PLC's memory map.

# Function to discover the PLC's IP address (basic network scan)
def discover_plc_ip():
    """
    Performs a basic network scan to find a PLC based on a known Modbus port (502)
    This is a simplified approach and may not work in all network configurations.
    """
    network_prefix = "192.168.1." # Adjust based on your network setup.
    for i in range(1, 255):  # Scan common IP address range
        ip_address = network_prefix + str(i)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1) # Short timeout to avoid blocking
            result = sock.connect_ex((ip_address, 502))  # Modbus port often used by PLCs
            if result == 0:
                print(f"Found potential PLC at: {ip_address}")
                sock.close()
                return ip_address # Return the IP address that responded.
            sock.close()
        except socket.error:
            pass # Connection refused or timeout, try the next IP.
    return None  # PLC not found in the scanned range.

def change_password(plc_ip, rack, slot, data_block, address, new_password, password_length):
    """
    Connects to the PLC, changes the password at the specified address, and disconnects.
    """
    try:
        plc = snap7.client.Client()
        plc.set_as_string(True) # Set data transfer to string format

        plc.connect(plc_ip, rack, slot)

        # Convert the new password to bytes, pad with null bytes if necessary
        password_bytes = new_password.encode('ascii')  # Use ascii or another compatible encoding
        padding_length = password_length - len(password_bytes)
        if padding_length > 0:
            password_bytes += b'\x00' * padding_length
        elif padding_length < 0:
            print("Error: Password too long.  Truncating.")
            password_bytes = password_bytes[:password_length]


        # Write the new password to the PLC's memory (Data Block)
        plc.db_write(data_block, address, password_bytes) # Important:  Use db_write!

        print(f"Password changed successfully on PLC {plc_ip} at DB{data_block}.{address} to: {new_password}")

        plc.disconnect()
        print("Disconnected from PLC.")

    except snap7.exceptions.Snap7Exception as e:
        print(f"Error communicating with PLC: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



# Main execution
if __name__ == "__main__":
    # Discover the PLC's IP address if it's not known.
    if PLC_IP is None:
        print("Discovering PLC IP address...")
        PLC_IP = discover_plc_ip()
        if PLC_IP is None:
            print("PLC IP address not found.  Please manually set PLC_IP and rerun the script.")
            exit()
        else:
            print(f"PLC IP address found: {PLC_IP}")

    # Perform the password change.
    change_password(PLC_IP, RACK, SLOT, PASSWORD_DATA_BLOCK, PASSWORD_ADDRESS, NEW_PASSWORD, PASSWORD_LENGTH)