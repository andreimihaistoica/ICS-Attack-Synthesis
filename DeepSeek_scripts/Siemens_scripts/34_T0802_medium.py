import snap7
import socket
from snap7.util import *
from snap7.types import *

def discover_plc_ip():
    """
    Scan the local network to discover the Siemens S7-1200 PLC's IP address.
    """
    # Example: Scan a range of IP addresses (adjust the range as needed)
    base_ip = "192.168.0."
    for i in range(1, 255):
        ip = base_ip + str(i)
        try:
            # Create a socket to check if the IP is reachable
            socket.create_connection((ip, 102), timeout=1)
            print(f"Found potential PLC at IP: {ip}")
            return ip
        except:
            continue
    return None

def collect_plc_info(plc_ip):
    """
    Connect to the PLC and collect information.
    """
    try:
        # Create a Snap7 client
        client = snap7.client.Client()
        client.connect(plc_ip, 0, 1)  # Connect to the PLC (rack=0, slot=1)

        # Get PLC information
        plc_info = client.get_cpu_info()
        print(f"PLC Name: {plc_info.ModuleName}")
        print(f"PLC Serial Number: {plc_info.SerialNumber}")
        print(f"PLC Firmware Version: {plc_info.ASName}")

        # Example: Read data from a DB (Data Block)
        db_number = 1  # Adjust the DB number as needed
        db_size = 100  # Adjust the size as needed
        db_data = client.db_read(db_number, 0, db_size)
        print(f"Data from DB{db_number}: {db_data}")

        # Disconnect from the PLC
        client.disconnect()
    except Exception as e:
        print(f"Error connecting to PLC: {e}")

if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("PLC IP address not found. Please check the network.")
        exit(1)

    print(f"Discovered PLC IP: {plc_ip}")

    # Step 2: Collect information from the PLC
    collect_plc_info(plc_ip)