import snap7
import socket
import struct
import subprocess
import re  # Regular expression library

# Configuration - Modify these based on your environment
PLC_IP = None  # Will be discovered if None
PLC_RACK = 0
PLC_SLOT = 1
NEW_PASSWORD = "NewStrongPassword123!"  # Replace with a strong password
PASSWORD_DB_NUMBER = 10  # Replace with the actual DB number holding the password
PASSWORD_OFFSET = 0      # Replace with the actual offset within the DB where the password starts
PASSWORD_LENGTH = 64      # Replace with the actual length of the password field in the DB (bytes)  -  Important: Consider encoding (e.g., ASCII = 1 byte per char, UTF-16 = 2 bytes per char)


def find_plc_ip():
    """
    Discovers the PLC IP address on the network.
    This is a rudimentary method and might need adjustment based on network setup.

    Returns:
        str: The PLC's IP address, or None if not found.
    """

    # Attempt to ping a broadcast address and then scan ARP table.  More reliable than UDP broadcast alone
    try:
        subprocess.run(["ping", "-b", "-c", "1", "255.255.255.255"], timeout=5, check=False, capture_output=True)  # Send a single ping to broadcast

        # Scan the ARP table
        arp_output = subprocess.check_output(["arp", "-a"]).decode("utf-8")
        for line in arp_output.splitlines():
            if "S7" in line or "Siemens" in line:  # Heuristic: Look for Siemens/S7 in ARP output
                match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None

    print("PLC IP address discovery failed.  Check network and ARP configuration.")
    return None

def encode_password(password, encoding='ascii'): # Or 'utf-16' if that is being used
    """
    Encodes the password string into bytes, padding with null bytes if needed.
    """
    encoded_password = password.encode(encoding)
    padding_needed = PASSWORD_LENGTH - len(encoded_password)

    if padding_needed > 0:
        encoded_password += b'\x00' * padding_needed  # Pad with null bytes
    elif padding_needed < 0:
        raise ValueError("Password too long for the allocated space in the database.")

    return encoded_password


def change_plc_password(plc_ip, rack, slot, db_number, offset, password_bytes):
    """
    Changes the password stored in a PLC data block.

    Args:
        plc_ip (str): IP address of the PLC.
        rack (int): PLC rack number.
        slot (int): PLC slot number.
        db_number (int): Data block number.
        offset (int): Byte offset within the data block.
        password_bytes (bytes): The new password encoded as bytes.  Must be the correct length.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)

        # Read existing data block (important for not corrupting other data)
        db = plc.db_read(db_number, 0, PASSWORD_LENGTH)

        # Overwrite password bytes
        db = db[:offset] + password_bytes + db[offset + len(password_bytes):] # Crucial: Preserve data around the password
        plc.db_write(db_number, 0, db)

        plc.disconnect()
        print(f"Successfully changed password on PLC {plc_ip}, DB{db_number} at offset {offset}.")

    except Exception as e:
        print(f"Error changing password on PLC {plc_ip}: {e}")


if __name__ == "__main__":

    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("Failed to discover PLC IP address.  Please set PLC_IP manually in the script.")
            exit(1)
        else:
            print(f"PLC IP address discovered: {PLC_IP}")


    try:
        encoded_password = encode_password(NEW_PASSWORD)
        change_plc_password(PLC_IP, PLC_RACK, PLC_SLOT, PASSWORD_DB_NUMBER, PASSWORD_OFFSET, encoded_password)

    except ValueError as ve:
        print(f"Password encoding error: {ve}")
    except Exception as e:
        print(f"General error: {e}")