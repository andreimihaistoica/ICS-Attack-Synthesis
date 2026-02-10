import socket
import struct
import time
from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the target IP range to scan
    ip_range = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]
    
    # Parse the response to find the PLC
    for sent, received in result:
        # Check if the received IP is the PLC (you might need to adjust this based on your network)
        if is_plc(received.psrc):
            return received.psrc
    
    return None

# Function to check if the IP is a PLC (you might need to adjust this based on your network)
def is_plc(ip):
    # Example: Check if the IP is in a known PLC range
    known_plc_ips = ["192.168.1.100", "192.168.1.101"]
    return ip in known_plc_ips

# Function to modify the PLC program
def modify_plc_program(plc_ip):
    # Create a Modbus client
    client = ModbusClient(host=plc_ip, port=502, auto_open=True, auto_close=True)
    
    # Connect to the PLC
    if not client.is_open():
        if not client.open():
            print(f"Unable to connect to PLC at {plc_ip}")
            return
    
    print(f"Connected to PLC at {plc_ip}")
    
    # Example: Modify a specific register (you might need to adjust this based on your PLC)
    register_address = 0x0001
    new_value = 0x1234  # Example value to write
    
    # Write the new value to the register
    if client.write_single_register(register_address, new_value):
        print(f"Modified register {register_address} to {new_value}")
    else:
        print(f"Failed to modify register {register_address}")
    
    # Close the connection
    client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
        # Modify the PLC program
        modify_plc_program(plc_ip)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()