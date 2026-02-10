from scapy.all import ARP, Ether, srp

def find_plc_ip(interface, ip_range):
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

    return devices

if __name__ == "__main__":
    interface = "eth0"  # Replace with your network interface
    ip_range = "192.168.1.0/24"  # Replace with your network range

    devices = find_plc_ip(interface, ip_range)
    print("Available devices in the network:")
    for device in devices:
        print(f"IP: {device['ip']}, MAC: {device['mac']}")

    # Assuming the PLC has a specific MAC address or IP, you can filter it out
    plc_ip = None
    for device in devices:
        if device['mac'] == "00:11:22:33:44:55":  # Replace with the PLC's MAC address
            plc_ip = device['ip']
            break

    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
    else:
        print("PLC not found in the network.")