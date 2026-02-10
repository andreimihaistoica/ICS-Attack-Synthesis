import socket
import subprocess
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Use a network scanning tool to find the PLC's IP address
    # This example uses the `nmap` tool, which must be installed on the system
    nmap_command = "nmap -p 502 --open 192.168.1.0/24"  # Adjust the subnet as needed
    result = subprocess.run(nmap_command, shell=True, capture_output=True, text=True)
    
    # Parse the output to find the IP address
    for line in result.stdout.splitlines():
        if "502/tcp open" in line:
            ip_address = line.split()[0]
            return ip_address
    
    return None

# Function to collect point and tag values from the PLC
def collect_point_and_tag_values(plc_ip):
    try:
        client = ModbusTcpClient(plc_ip)
        client.connect()
        
        # Example: Read holding registers (0x03) from address 0 to 10
        result = client.read_holding_registers(0, 10, unit=1)
        
        if result.isError():
            print("Error reading registers")
        else:
            print("Collected Point and Tag Values:")
            for i, value in enumerate(result.registers):
                print(f"Register {i}: {value}")
        
        client.close()
    except ConnectionException as e:
        print(f"Connection error: {e}")

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        collect_point_and_tag_values(plc_ip)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()