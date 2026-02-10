import subprocess
import socket
from pymodbus.client import ModbusTcpClient

# Function to find the PLC's IP address
def find_plc_ip():
    # Use nmap to scan the network for devices
    nmap_output = subprocess.check_output(['nmap', '-sn', '192.168.1.0/24']).decode('utf-8')
    devices = nmap_output.split('\n')
    
    # Filter out the IP addresses
    ip_addresses = [line.split()[1] for line in devices if 'Nmap scan report for' in line]
    
    # Assume the PLC is the first device found (you may need to refine this)
    if ip_addresses:
        return ip_addresses[0]
    else:
        raise Exception("No devices found on the network")

# Function to change the PLC's operating mode to "Program"
def change_operating_mode_to_program(plc_ip):
    # Connect to the PLC
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        raise Exception(f"Failed to connect to PLC at {plc_ip}")
    
    # Define the register address for changing the operating mode
    # This address may vary depending on the PLC model and vendor
    operating_mode_register = 0x0000  # Example register address
    
    # Define the value for "Program" mode
    program_mode_value = 0x0001  # Example value for "Program" mode
    
    # Write the value to the register to change the operating mode
    result = client.write_register(operating_mode_register, program_mode_value)
    
    if result.isError():
        raise Exception(f"Failed to change operating mode to Program: {result}")
    
    print(f"Operating mode changed to Program on PLC at {plc_ip}")
    
    # Close the connection
    client.close()

# Main function
def main():
    try:
        # Find the PLC's IP address
        plc_ip = find_plc_ip()
        print(f"PLC found at IP address: {plc_ip}")
        
        # Change the operating mode to "Program"
        change_operating_mode_to_program(plc_ip)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()