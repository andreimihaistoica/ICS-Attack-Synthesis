import socket
import subprocess
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Use ARP scan to find devices on the network
    result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if 'dynamic' in line:
            ip = line.split()[0]
            # Check if the IP is a valid PLC IP (you can add more checks if needed)
            if is_plc_ip(ip):
                return ip
    return None

# Function to check if an IP is a valid PLC IP
def is_plc_ip(ip):
    # Example check: you can add more specific checks based on your network setup
    try:
        client = ModbusTcpClient(ip)
        client.connect()
        if client.is_socket_open():
            client.close()
            return True
    except ConnectionException:
        pass
    return False

# Function to get the operating mode of the PLC
def get_plc_operating_mode(ip):
    try:
        client = ModbusTcpClient(ip)
        client.connect()
        
        # Read the operating mode from the PLC (assuming it's stored in a specific register)
        # The register address and data type may vary depending on the PLC model
        result = client.read_holding_registers(address=0x0000, count=1, unit=1)
        
        if result.isError():
            print("Error reading operating mode from PLC")
            return None
        
        mode = result.registers[0]
        
        # Map the mode value to a human-readable string
        mode_map = {
            0: 'Stop',
            1: 'Run',
            2: 'Program',
            3: 'Remote',
            4: 'Reset',
            5: 'Test/Monitor'
        }
        
        return mode_map.get(mode, 'Unknown')
    except ConnectionException:
        print("Failed to connect to PLC")
        return None
    finally:
        client.close()

# Main function
def main():
    print("Discovering PLC IP address...")
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        print("Getting PLC operating mode...")
        operating_mode = get_plc_operating_mode(plc_ip)
        if operating_mode:
            print(f"PLC Operating Mode: {operating_mode}")
        else:
            print("Failed to get PLC operating mode")
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()