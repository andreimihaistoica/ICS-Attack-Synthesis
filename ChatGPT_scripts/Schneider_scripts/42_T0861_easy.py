import socket
import ipaddress
from pymodbus.client.sync import ModbusTcpClient

def find_plc_ip(subnet):
    """
    Discovers the IP address of the PLC within the specified subnet.
    Uses a network scan to find Modbus-compatible units.
    """
    print(f"Scanning subnet {subnet} for PLC...")
    for ip in ipaddress.IPv4Network(subnet, strict=False):
        ip = str(ip)
        try:
            # Open a socket to check for Modbus TCP response (port 502 is default)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # Short timeout for faster scans
            result = sock.connect_ex((ip, 502))
            if result == 0:  # PLC Modbus TCP port is open
                print(f"Found possible PLC at {ip}")
                sock.close()
                return ip
        except Exception as e:
            pass  # Ignore unreachable IPs
        finally:
            sock.close()
    print("No PLC found in the specified subnet.")
    return None


def collect_modbus_tags(plc_ip):
    """
    Connects to the PLC via Modbus TCP to read point/tag information.
    For demonstration, this script reads a range of Modbus memory addresses.
    """
    print(f"Connecting to PLC at {plc_ip} and collecting point/tag data...")
    client = ModbusTcpClient(plc_ip)

    if client.connect():  # Establish connection with PLC
        try:
            # Example: Read Holding Registers (Memory Address Range 0–10)
            response = client.read_holding_registers(0, 10, unit=1)
            if response.isError():
                print(f"Error reading from PLC {plc_ip}: {response}")
            else:
                # Display raw values read from the PLC
                print("Collected Point/Tag Values:")
                for i, value in enumerate(response.registers):
                    print(f"Tag {i}: {value}")
        finally:
            client.close()
    else:
        print(f"Could not connect to the PLC at {plc_ip}.")


if __name__ == "__main__":
    # Define subnet to scan, modify as per environment (e.g., "192.168.1.0/24")
    subnet_to_scan = "192.168.1.0/24"

    # Step 1: Find PLC IP address
    plc_ip = find_plc_ip(subnet_to_scan)

    # Step 2: If found, collect tags/points
    if plc_ip:
        collect_modbus_tags(plc_ip)
    else:
        print("Failed to locate the PLC. Exiting.")