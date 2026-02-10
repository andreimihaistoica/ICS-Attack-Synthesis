from pycomm3 import LogixDriver
from scapy.all import ARP, Ether, srp
import socket

def find_plc_ip():
    # Create an ARP request packet
    arp = ARP(pdst="192.168.1.0/24")  # Adjust the subnet as per your network
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC's IP
    for sent, received in result:
        try:
            # Attempt to connect to the device to confirm it's the PLC
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((received.psrc, 44818))  # Port 44818 is typically used for Rockwell PLCs
                return received.psrc
        except:
            continue
    return None

def collect_tags_and_points(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            print(f"Connected to PLC at {plc_ip}")

            # Get the list of tags
            tags = plc.get_tag_list()
            print(f"Found {len(tags)} tags.")

            # Collect tag values
            for tag in tags:
                tag_name = tag['tag_name']
                tag_value = plc.read(tag_name)
                print(f"Tag: {tag_name}, Value: {tag_value}")

    except Exception as e:
        print(f"Error: {e}")

def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")
        
        # Step 2: Collect tags and points
        collect_tags_and_points(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()