import subprocess
import re
import socket
import struct
import time
from pysnmp.hlapi import *
from pymodbus.client.sync import ModbusTcpClient

# Function to discover the PLC's IP address using ARP scan
def discover_plc_ip():
    # Run ARP scan to find devices on the network
    arp_result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
    arp_output = arp_result.stdout

    # Regular expression to find IP and MAC addresses
    ip_mac_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+([\w-]+)')
    devices = ip_mac_pattern.findall(arp_output)

    # Filter out the PLC based on known MAC address (example: 00-14-22-01-23-45)
    known_plc_mac = '00-14-22-01-23-45'
    for ip, mac in devices:
        if mac.lower() == known_plc_mac.lower():
            return ip

    return None

# Function to change the PLC's credentials using Modbus
def change_plc_credentials(plc_ip, new_password):
    # Connect to the PLC using Modbus
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return

    # Example Modbus register to change the password (this is a placeholder)
    password_register = 0x1000

    # Convert the new password to a byte array
    password_bytes = new_password.encode('utf-8')
    password_length = len(password_bytes)

    # Write the new password to the PLC
    try:
        client.write_registers(password_register, [struct.unpack('!H', password_bytes[i:i+2])[0] for i in range(0, password_length, 2)])
        print(f"Password changed to {new_password}")
    except Exception as e:
        print(f"Failed to change password: {e}")

    client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("PLC not found on the network")
        return

    print(f"PLC found at IP address: {plc_ip}")

    # New password to set
    new_password = "NewSecurePassword123"

    # Change the PLC's credentials
    change_plc_credentials(plc_ip, new_password)

if __name__ == "__main__":
    main()