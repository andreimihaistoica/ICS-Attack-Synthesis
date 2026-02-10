import socket
import struct
import sys
import time

# Configuration (Update these if necessary)
PLC_IP = "192.168.9.24"  # Default IP. Will be overridden if IP discovery works.
PLC_PORT = 502  # Standard Modbus port for Schneider PLCs
MODBUS_UNIT_ID = 255  # Unit ID, Schneider Electric uses 255.
# The Modbus Unit ID is a single byte (0-255) that serves to identify a device behind a gateway/router, 
# similar to IP Address, but in the Modbus context. The client must set the Unit ID each time it connects.
# For some equipment, you may need to modify the Unit ID on the field device's control panel or HMI.
# If no value is provided by the user, then the client uses a default value of 1. Schneider PLCs use the default value of 255.

# Modbus Function Codes
READ_HOLDING_REGISTERS = 0x03
WRITE_SINGLE_REGISTER = 0x06

# Schneider Electric Specific (May need adjustments for different models/firmware)
# Address of the Operating Mode register (Consult PLC documentation)
OPERATING_MODE_REGISTER = 0x6000 # Example Address (Decimal 24576).
# In the Schneider Electric PLC, the operating mode is generally located in Holding Register 24576 (hexadecimal 0x6000)


# Operating Mode Values (Consult PLC documentation)
PROGRAM_MODE = 8 # Example Value
RUN_MODE = 9     # Example Value
STOP_MODE = 10    # Example Value

def discover_plc_ip():
    """Attempts to discover the PLC IP address by sending a broadcast UDP message.

    This is a basic attempt and might not work in all network configurations.  It assumes
    the PLC responds to a specific broadcast message with its IP address.
    """
    BROADCAST_ADDRESS = '255.255.255.255'  # Use your network's broadcast address
    DISCOVERY_PORT = 30000  # Example port, adjust to your PLC's discovery protocol
    DISCOVERY_MESSAGE = b"PLC_DISCOVERY"  # Example message, adjust as needed
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(5) # Timeout after 5 seconds

        sock.sendto(DISCOVERY_MESSAGE, (BROADCAST_ADDRESS, DISCOVERY_PORT))
        print(f"Sent discovery message to {BROADCAST_ADDRESS}:{DISCOVERY_PORT}")

        try:
            data, addr = sock.recvfrom(1024)
            print(f"Received response from {addr}: {data.decode()}")
            return addr[0]  # Return the IP address from the response
        except socket.timeout:
            print("No response received from PLC within the timeout.")
            return None

    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None
    finally:
        sock.close()

def create_modbus_frame(unit_id, function_code, address, value=None):
    """Creates a Modbus RTU frame (without CRC)."""
    frame = bytes([unit_id, function_code])  # Unit ID and Function Code
    frame += struct.pack(">H", address)      # Address (Big-endian unsigned short)

    if function_code == WRITE_SINGLE_REGISTER:
        frame += struct.pack(">H", value)  # Value (Big-endian unsigned short)

    return frame

def calculate_crc(data):
    """Calculates the Modbus CRC16."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, 'little') # Little-endian byte order


def send_modbus_request(plc_ip, plc_port, modbus_frame):
    """Sends a Modbus request to the PLC and returns the response."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5) # Set a timeout for the connection
        sock.connect((plc_ip, plc_port))
        
        # Add CRC to the frame:
        crc = calculate_crc(modbus_frame)
        modbus_frame += crc
        
        sock.sendall(modbus_frame)
        response = sock.recv(1024) # Buffer size
        return response

    except socket.timeout:
        print("Connection timed out.")
        return None
    except ConnectionRefusedError:
        print("Connection refused. Ensure the PLC is running and accessible.")
        return None
    except Exception as e:
        print(f"Error communicating with PLC: {e}")
        return None
    finally:
        if sock:
            sock.close()


def change_operating_mode(plc_ip, plc_port, unit_id, mode):
    """Changes the operating mode of the PLC."""
    if mode not in [PROGRAM_MODE, RUN_MODE, STOP_MODE]:
        print("Invalid operating mode.")
        return False

    # Create the Modbus frame to write the operating mode register
    modbus_frame = create_modbus_frame(unit_id, WRITE_SINGLE_REGISTER, OPERATING_MODE_REGISTER, mode)

    # Send the Modbus request to the PLC
    response = send_modbus_request(plc_ip, plc_port, modbus_frame)

    if response:
        # Basic response check (adjust as needed based on the PLC's Modbus implementation)
        if response[1] == WRITE_SINGLE_REGISTER: # Confirm correct function code in response
            print(f"Successfully changed PLC operating mode to {mode}.")
            return True
        else:
            print(f"Error changing operating mode.  Response: {response.hex()}")
            return False
    else:
        print("No response from PLC.")
        return False


if __name__ == "__main__":
    # 1. Attempt to Discover PLC IP
    discovered_ip = discover_plc_ip()
    if discovered_ip:
        PLC_IP = discovered_ip
        print(f"PLC IP address discovered: {PLC_IP}")
    else:
        print(f"PLC IP address discovery failed. Using configured IP: {PLC_IP}")

    # 2. Main Execution
    try:
        # Ask the user for the desired operating mode
        print("Available Operating Modes:")
        print(f"  {PROGRAM_MODE}: Program")
        print(f"  {RUN_MODE}: Run")
        print(f"  {STOP_MODE}: Stop")

        mode = int(input("Enter the desired operating mode (number): "))

        if change_operating_mode(PLC_IP, PLC_PORT, MODBUS_UNIT_ID, mode):
            print("Operating mode change successful.")
        else:
            print("Operating mode change failed.")

    except ValueError:
        print("Invalid input. Please enter a number for the operating mode.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")