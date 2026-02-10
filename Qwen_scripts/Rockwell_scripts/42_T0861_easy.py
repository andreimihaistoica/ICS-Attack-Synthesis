import socket
import struct
import subprocess
import ipaddress
from pymodbus.client import ModbusTcpClient

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1.0/24"
    
    # Use nmap to scan the subnet for devices
    nmap_command = f"nmap -sn {subnet}"
    result = subprocess.run(nmap_command, shell=True, capture_output=True, text=True)
    
    # Parse the nmap output to find the PLC's IP address
    for line in result.stdout.splitlines():
        if "Nmap scan report for" in line:
            ip = line.split()[-1]
            # Check if the IP is a valid IP address
            try:
                ipaddress.ip_address(ip)
                return ip
            except ValueError:
                continue
    return None

# Function to read point and tag values from the PLC
def read_plc_tags(plc_ip, tags):
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return
    
    for tag in tags:
        # Assuming tags are in the format (register_address, number_of_registers)
        register_address, number_of_registers = tag
        try:
            response = client.read_holding_registers(register_address, number_of_registers, unit=1)
            if response.isError():
                print(f"Error reading tag at address {register_address}")
            else:
                print(f"Tag at address {register_address}: {response.registers}")
        except Exception as e:
            print(f"Exception reading tag at address {register_address}: {e}")
    
    client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("Failed to discover PLC IP address")
        return
    
    print(f"Discovered PLC IP address: {plc_ip}")
    
    # Define the tags to read (register_address, number_of_registers)
    tags = [
        (0, 10),  # Example: Read 10 registers starting from address 0
        (100, 5), # Example: Read 5 registers starting from address 100
    ]
    
    # Read the tags from the PLC
    read_plc_tags(plc_ip, tags)

if __name__ == "__main__":
    main()