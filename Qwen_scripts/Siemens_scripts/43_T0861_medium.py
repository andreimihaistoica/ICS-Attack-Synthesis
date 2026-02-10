import pycomm3
from pycomm3 import LogixDriver
from scapy.all import ARP, Ether, srp
import ipaddress

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the target IP range (e.g., 192.168.1.0/24)
    ip_range = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]
    
    # Parse the response to find the PLC's IP address
    for sent, received in result:
        if "Siemens" in received.hwsrc:  # Assuming the PLC's MAC address contains "Siemens"
            return received.psrc
    
    return None

# Function to read tag values from the PLC
def read_tag_values(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            # List of tags to read (example tags)
            tags = ['Input1', 'Output1', 'MemoryLocation1', 'ProcessVariable1']
            
            # Read the tag values
            tag_values = plc.read(*tags)
            
            # Print the tag values
            for tag in tag_values:
                print(f"Tag: {tag.tag_name}, Value: {tag.value}")
    except Exception as e:
        print(f"Error reading tag values: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        # Read tag values from the PLC
        read_tag_values(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()