from pycomm3 import LogixDriver
import time

def find_plc_ip():
    """
    Scans the network to find the PLC's IP address.
    This is a placeholder function; implement your own logic for IP discovery.
    """
    # Example: Return a hardcoded IP address for demonstration purposes
    return "192.168.1.100"

def suppress_alarms(plc_ip):
    """
    Connects to the PLC and suppresses alarms by manipulating relevant tags.
    """
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            print(f"Connected to PLC at {plc_ip}")

            # Read the current state of the START and Activate_FanA tags
            start_state = plc.read("START")
            activate_fan_state = plc.read("Activate_FanA")

            print(f"Initial START state: {start_state}")
            print(f"Initial Activate_FanA state: {activate_fan_state}")

            # Suppress alarms by modifying the Activate_FanA tag
            print("Suppressing alarms by setting Activate_FanA to FALSE...")
            plc.write(("Activate_FanA", False))

            # Verify the change
            activate_fan_state = plc.read("Activate_FanA")
            print(f"Updated Activate_FanA state: {activate_fan_state}")

            # Optionally, suppress other alarms or modify other tags as needed
            # Example: Suppress the FanA_Off alarm
            print("Suppressing FanA_Off alarm by setting FanA_Off to FALSE...")
            plc.write(("FanA_Off", False))

            # Verify the change
            fan_off_state = plc.read("FanA_Off")
            print(f"Updated FanA_Off state: {fan_off_state}")

            # Keep the script running to maintain the suppressed state
            print("Alarms suppressed. Press Ctrl+C to exit.")
            while True:
                time.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("Failed to find the PLC's IP address.")
        return

    # Suppress alarms on the PLC
    suppress_alarms(plc_ip)

if __name__ == "__main__":
    main()