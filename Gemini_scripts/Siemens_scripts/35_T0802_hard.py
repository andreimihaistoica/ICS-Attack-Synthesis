import snap7
import time
import struct
import socket
import re

# Configuration - Replace with your actual values if different after IP discovery
# These are defaults based on typical S7-1200 configuration. Adjust as needed.
RACK = 0
SLOT = 1
MOTOR_TEMP_ADDRESS = 7 # MW7
ACTIVATE_FAN_A_ADDRESS = 0 #M0.0
ACTIVATE_FAN_B_ADDRESS = 0 #M0.1

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address on the local network.
    This is a rudimentary approach and might need refinement for complex networks.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """

    try:
        # Send a simple broadcast message (modify as needed)
        broadcast_address = '<broadcast>' # Use actual broadcast IP if needed
        port = 1771 # Siemens Discovery Protocol (CDP) port

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)  # Timeout after 2 seconds

        message = b'\xFE\xFE\x00\x00\x04\x01' # Example CDP query
        sock.sendto(message, (broadcast_address, port))

        data, addr = sock.recvfrom(1024)  # Adjust buffer size as needed

        # Extract IP address from response
        if data:
            # Simple regex to find potential IP address in the response
            match = re.search(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', data.decode('latin-1'))
            if match:
                return match.group(0)
            else:
                print("PLC Discovery: No IP address found in response.")
                return None
        else:
            print("PLC Discovery: No response from PLC.")
            return None

    except Exception as e:
        print(f"PLC Discovery Error: {e}")
        return None
    finally:
        if 'sock' in locals():
            sock.close()

def read_motor_temperature(plc, address):
    """Reads the motor temperature (INT) from the specified address.

    Args:
        plc: The Snap7 client object.
        address: The memory word address (e.g., 7 for MW7).

    Returns:
        int: The motor temperature, or None if an error occurred.
    """
    try:
        # Read 2 bytes (INT) from the memory word.  DB number is 0, so the read happens from PLC memory,
        #  address is relative to DB, here there isn't any DB so it is relative to memory.
        result = plc.read_area(snap7.constants.Areas.MK, 0, address, 2)
        # Unpack the bytes as a short (2-byte integer)
        temperature = struct.unpack(">h", result)[0] # ">h" for big-endian short

        return temperature
    except Exception as e:
        print(f"Error reading motor temperature: {e}")
        return None

def read_digital_output(plc, address):
    """Reads the state of a digital output (BOOL) from the specified address.

    Args:
        plc: The Snap7 client object.
        address: The memory byte address (e.g., 0 for M0.0, 1 for M0.1).

    Returns:
        bool: The state of the digital output (True/False), or None if an error occurred.
    """
    try:
        # Read 1 byte from the memory byte (M area).  DB number is 0 for system memory.
        result = plc.read_area(snap7.constants.Areas.MK, 0, address // 8, 1)

        # Extract the bit from the byte
        byte_value = result[0]
        bit_position = address % 8
        bit_value = (byte_value >> bit_position) & 1  # Right shift and mask

        return bool(bit_value)  # Convert 1/0 to True/False
    except Exception as e:
        print(f"Error reading digital output: {e}")
        return None

def main():
    plc_ip = find_plc_ip()

    if not plc_ip:
        print("Could not automatically discover PLC IP.  Please manually set the IP address.")
        plc_ip = input("Enter PLC IP Address: ")  #Or assign a default here, e.g.,  "192.168.1.10"
        if not plc_ip:
            print("No IP provided.  Exiting.")
            return


    plc = snap7.client.Client()
    try:
        plc.connect(plc_ip, RACK, SLOT)
        print(f"Connected to PLC at {plc_ip}")

        #Collection phase - example reads. Extend as needed based on the prompt.
        motor_temp = read_motor_temperature(plc, MOTOR_TEMP_ADDRESS)
        if motor_temp is not None:
            print(f"Motor Temperature: {motor_temp}")

        fan_a_active = read_digital_output(plc, ACTIVATE_FAN_A_ADDRESS)
        if fan_a_active is not None:
            print(f"Fan A Active: {fan_a_active}")

        fan_b_active = read_digital_output(plc, ACTIVATE_FAN_B_ADDRESS)
        if fan_b_active is not None:
            print(f"Fan B Active: {fan_b_active}")

        # Add more data collection as required.
        # This is just a minimal example based on the provided code and prompt.

    except Exception as e:
        print(f"Error connecting or communicating with PLC: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")

if __name__ == "__main__":
    main()