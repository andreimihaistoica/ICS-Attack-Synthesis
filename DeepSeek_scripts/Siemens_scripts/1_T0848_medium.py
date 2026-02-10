from scapy.all import ARP, Ether, srp

def scan_network(ip_range):
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    return devices

if __name__ == "__main__":
    ip_range = "192.168.1.1/24"  # Adjust this to your network's IP range
    print("Scanning network for devices...")
    devices = scan_network(ip_range)
    print("Available devices in the network:")
    print("IP Address\t\tMAC Address")
    for device in devices:
        print(f"{device['ip']}\t\t{device['mac']}")