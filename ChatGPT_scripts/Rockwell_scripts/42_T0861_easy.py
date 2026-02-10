from pymodbus.client.sync import ModbusTcpClient
import socket
import struct
import ipaddress

def scan_for_plc(subnet):
    """
    Scans the subnet to discover the PLC's IP address.
    """
    print(f"Scanning for the PLC on subnet {subnet}")
    discovered_ip = None

    # Loop through all IPs in the subnet
    for ip in ipaddress.ip_network(subnet).hosts():
        try:
            # Attempt to connect on Modbus TCP port (502)
            client = ModbusTcpClient(str(ip), port=502, timeout=0.5)
            if client.connect():
                print(f"PLC found at IP address: {ip}")
                discovered_ip = str(ip)
                client.close()
                break
        except:
            # Ignore connection errors
            pass

    if discovered_ip is None:
        print("No PLC found on the network.")
    return discovered_ip

def collect_tags_and_points(plc_ip):
    """
    Connects to the PLC to read memory registers and extract tags/points.
    """
    try:
        print(f"Connecting to PLC at {plc_ip}...")
        client = ModbusTcpClient(plc_ip, port=502)
        if not client.connect():
            print("Failed to connect to the PLC.")
            return

        print(f"Collecting tags and points from PLC at {plc_ip}")
        
        # Example: Query holding registers (start=0, count=10)
        start_address = 0
        count = 10
        result = client.read_holding_registers(start_address, count, unit=0x01)
        
        if result.isError():
            print("Error reading registers.")
        else:
            # Display collected registers
            print(f"Registers ({start_address}-{start_address+count-1}): {result.registers}")

        client.close()
    except Exception as e:
        print(f"Error collecting tags and points: {e}")

if __name__ == "__main__":
    # Define the subnet to scan for the PLC (e.g., '192.168.1.0/24')
    subnet = '192.168.1.0/24'

    # Step 1: Find the PLC's IP address
    plc_ip = scan_for_plc(subnet)

    # Step 2: Connect to the PLC and collect data
    if plc_ip:
        collect_tags_and_points(plc_ip)
    else:
        print("Aborting as no PLC was discovered on the network.")