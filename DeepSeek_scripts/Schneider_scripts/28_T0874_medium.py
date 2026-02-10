from scapy.all import ARP, Ether, srp

def find_plc_ip():
    # Define the network range to scan
    ip_range = "192.168.1.1/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]
    
    # Parse the response to find the PLC's IP address
    plc_ip = None
    for sent, received in result:
        # Assuming the PLC has a specific MAC address prefix (e.g., 00:80:9F)
        if received.hwsrc.startswith("00:80:9F"):
            plc_ip = received.psrc
            break
    
    return plc_ip

# Find the PLC's IP address
plc_ip = find_plc_ip()
if plc_ip:
    print(f"Found PLC at IP: {plc_ip}")
else:
    print("PLC not found on the network.")
    exit(1)