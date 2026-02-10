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
    result = srp(packet, timeout=3, verbose=0)[0]

    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Filter out the PLC based on known MAC address or other criteria
    plc_ip = None
    for device in devices:
        if device['mac'] == "00:11:22:33:44:55":  # Replace with the actual PLC MAC address
            plc_ip = device['ip']
            break

    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
    else:
        print("PLC not found on the network.")

    return plc_ip

plc_ip = find_plc_ip()