import snap7
import time
import socket
import struct

# Configuration - Modify these if needed.  However, the script attempts to find the PLC IP automatically.
PLC_RACK = 0
PLC_SLOT = 1
FIRMWARE_UPDATE_MODE_MB = 0  # Modify if the memory bit for firmware update mode is different
FIRMWARE_UPDATE_MODE_OFFSET = 0  # Offset of the bit within the byte

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address on the network.
    This is a basic discovery method and may not work in all network configurations.
    It relies on broadcasting a simple packet and listening for a response.
    """
    broadcast_address = '<broadcast>' # Use broadcast address. Replace if broadcasting isn't appropriate for the network
    port = 161  #Standard port for SNMP GET requests for system description
    message = b'\x30\x26\x02\x01\x01\x04\x06public\xa0\x19\x02\x04\x76\x44\x19\x27\x02\x01\x00\x02\x01\x00\x30\x0b\x30\x09\x06\x05\x2b\x06\x01\x02\x01\x01\x00\x05\x00'

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Enable broadcasting
        sock.settimeout(5)  # Timeout after 5 seconds.  Adjust as needed.

        sock.sendto(message, (broadcast_address, port))

        print("Broadcasting request to find PLC...")
        data, addr = sock.recvfrom(1024) # Increased buffer size.

        plc_ip = addr[0]
        print(f"PLC IP address found: {plc_ip}")
        return plc_ip

    except socket.timeout:
        print("No response received. PLC may not be discoverable via broadcast or network configuration prevents this.")
        return None
    except Exception as e:
        print(f"An error occurred during PLC discovery: {e}")
        return None
    finally:
        sock.close()


def activate_firmware_update_mode(plc_ip):
    """
    Activates firmware update mode by setting a specific memory bit in the PLC.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)

        # Read the current value of the memory byte.  This is important!
        mb_data = plc.read_area(snap7.constants.Areas.MK, 0, FIRMWARE_UPDATE_MODE_MB, 1) #Read one byte.

        # Get the current value of the byte
        current_byte = mb_data[0]

        # Set the specific bit within the byte to 1 (activate firmware update mode)
        new_byte = current_byte | (1 << FIRMWARE_UPDATE_MODE_OFFSET)

        # Prepare the data to be written back to the PLC
        data_to_write = bytearray([new_byte])

        # Write the modified byte back to the PLC
        plc.write_area(snap7.constants.Areas.MK, 0, FIRMWARE_UPDATE_MODE_MB, data_to_write)

        print(f"Firmware update mode activated on PLC {plc_ip} (MB{FIRMWARE_UPDATE_MODE_MB}.{FIRMWARE_UPDATE_MODE_OFFSET})")

        # Disconnect from the PLC
        plc.disconnect()


    except snap7.exceptions.Snap7Exception as e:
        print(f"Error communicating with PLC {plc_ip}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def deactivate_firmware_update_mode(plc_ip):
    """
    Deactivates firmware update mode by clearing a specific memory bit in the PLC.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)

        # Read the current value of the memory byte.
        mb_data = plc.read_area(snap7.constants.Areas.MK, 0, FIRMWARE_UPDATE_MODE_MB, 1) #Read one byte.

        # Get the current value of the byte
        current_byte = mb_data[0]

        # Clear the specific bit within the byte (deactivate firmware update mode)
        new_byte = current_byte & ~(1 << FIRMWARE_UPDATE_MODE_OFFSET)

        # Prepare the data to be written back to the PLC
        data_to_write = bytearray([new_byte])

        # Write the modified byte back to the PLC
        plc.write_area(snap7.constants.Areas.MK, 0, FIRMWARE_UPDATE_MODE_MB, data_to_write)


        print(f"Firmware update mode deactivated on PLC {plc_ip} (MB{FIRMWARE_UPDATE_MODE_MB}.{FIRMWARE_UPDATE_MODE_OFFSET})")

        # Disconnect from the PLC
        plc.disconnect()

    except snap7.exceptions.Snap7Exception as e:
        print(f"Error communicating with PLC {plc_ip}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        # Example Usage:
        print("Activating Firmware Update Mode...")
        activate_firmware_update_mode(plc_ip)
        time.sleep(5)  # Simulate the PLC being in this mode for a while. Adjust as necessary.
        print("Deactivating Firmware Update Mode...")
        deactivate_firmware_update_mode(plc_ip)
    else:
        print("Could not find PLC IP address.  Please check network configuration and broadcasting settings.")