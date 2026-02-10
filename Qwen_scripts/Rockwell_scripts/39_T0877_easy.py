import socket
import struct
from pymodbus.client import ModbusTcpClient
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the target IP range to scan (e.g., 192.168.1.0/24)
    target_ip = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=target_ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]
    
    # Parse the response to find the PLC's IP address
    for sent, received in result:
        # You can add additional checks to identify the PLC (e.g., MAC address, device name)
        print(f"IP: {received.psrc} - MAC: {received.hwsrc}")
        # For demonstration, we assume the first device found is the PLC
        return received.psrc

# Function to read the I/O Image from the PLC
def read_io_image(plc_ip, start_address, count):
    try:
        # Create a Modbus TCP client
        client = ModbusTcpClient(plc_ip)
        
        # Connect to the PLC
        if client.connect():
            print(f"Connected to PLC at {plc_ip}")
            
            # Read the I/O Image (e.g., holding registers)
            response = client.read_holding_registers(start_address, count, unit=1)
            
            if response.isError():
                print("Error reading I/O Image")
            else:
                print("I/O Image:")
                for i, value in enumerate(response.registers):
                    print(f"Address {start_address + i}: {value}")
            
            # Close the connection
            client.close()
        else:
            print(f"Failed to connect to PLC at {plc_ip}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
        
        # Define the start address and number of registers to read
        start_address = 0  # Example start address
        count = 10         # Example number of registers to read
        
        # Read the I/O Image
        read_io_image(plc_ip, start_address, count)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()