from scapy.all import ARP, Ether, srp

def find_plc_ip(interface='eth0'):
    # Define the IP range to scan
    ip_range = "192.168.1.0/24"  # Adjust this to your network

    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and capture the response
    result = srp(packet, timeout=2, iface=interface, verbose=False)[0]

    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Filter for the PLC (assuming you know the MAC address or vendor OUI)
    plc_ip = None
    for device in devices:
        if device['mac'].startswith("00:0E:CF"):  # Example MAC prefix for Siemens
            plc_ip = device['ip']
            break

    return plc_ip

# Example usage
plc_ip = find_plc_ip()
if plc_ip:
    print(f"PLC IP Address: {plc_ip}")
else:
    print("PLC not found on the network.")