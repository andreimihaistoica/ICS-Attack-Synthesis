import socket
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the IP address
            client = ModbusTcpClient(ip)
            client.connect()
            if client.is_socket_open():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except ConnectionException:
            continue
    print("PLC not found in the specified subnet.")
    return None

# Function to collect point and tag values
def collect_point_and_tag_values(plc_ip):
    client = ModbusTcpClient(plc_ip)
    try:
        client.connect()
        if not client.is_socket_open():
            print("Failed to connect to the PLC.")
            return

        # Example: Collecting values from holding registers (0x0000 to 0x0009)
        start_address = 0x0000
        count = 10
        response = client.read_holding_registers(start_address, count, unit=1)

        if response.isError():
            print("Error reading registers.")
            return

        # Print the collected values
        print("Collected Point and Tag Values:")
        for i, value in enumerate(response.registers):
            print(f"Register {start_address + i}: {value}")

    except ConnectionException as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        collect_point_and_tag_values(plc_ip)

if __name__ == "__main__":
    main()