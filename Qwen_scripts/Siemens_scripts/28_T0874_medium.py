from scapy.all import ARP, Ether, srp
import socket

def find_plc_ip():
    # Define the target IP range to scan
    target_ip = "192.168.1.0/24"  # Adjust this to your network

    # Create an ARP request packet
    arp = ARP(pdst=target_ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]

    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Filter the devices to find the PLC
    plc_ip = None
    for device in devices:
        try:
            hostname = socket.gethostbyaddr(device['ip'])[0]
            if "plc" in hostname.lower():  # Adjust this condition based on your PLC's hostname
                plc_ip = device['ip']
                break
        except socket.herror:
            continue

    return plc_ip

plc_ip = find_plc_ip()
if plc_ip:
    print(f"PLC IP Address: {plc_ip}")
else:
    print("PLC not found on the network.")