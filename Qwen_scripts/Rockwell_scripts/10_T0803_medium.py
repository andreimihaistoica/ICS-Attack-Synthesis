from scapy.all import ARP, Ether, srp
import ipaddress

def discover_plc_ip(subnet):
    # Create an ARP request packet
    arp = ARP(pdst=subnet)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]

    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Filter for the PLC (assuming the PLC has a specific MAC address or vendor OUI)
    plc_ip = None
    for device in devices:
        if device['mac'].startswith('00:80:e1'):  # Example MAC address prefix for Rockwell PLC
            plc_ip = device['ip']
            break

    return plc_ip

# Example usage
subnet = "192.168.1.0/24"  # Replace with your network subnet
plc_ip = discover_plc_ip(subnet)
if plc_ip:
    print(f"PLC IP Address: {plc_ip}")
else:
    print("PLC not found on the network.")