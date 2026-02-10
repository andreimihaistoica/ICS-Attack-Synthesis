import socket
import struct
from pymodbus.client import ModbusTcpClient
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the target IP range to scan
    target_ip = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=target_ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]
    
    # Parse the response to find the PLC
    for sent, received in result:
        if received.psrc == "192.168.1.100":  # Replace with the known IP of the PLC
            return received.psrc
    return None

# Function to perform an online edit to the PLC
def online_edit_plc(plc_ip):
    # Connect to the PLC
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print("Failed to connect to the PLC.")
        return
    
    try:
        # Example: Modify a specific register (e.g., holding register 0x0001)
        register_address = 0x0001
        new_value = 0x1234  # Example value to write
        
        # Write the new value to the register
        result = client.write_register(register_address, new_value)
        if result.isError():
            print("Failed to write to the register.")
        else:
            print(f"Successfully wrote {new_value} to register {register_address}.")
    
    finally:
        client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        # Perform the online edit
        online_edit_plc(plc_ip)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()